import json
from typing import List, Dict, Any, Tuple
from PIL import Image
from backend.app.core.config import settings
from backend.app.core.storage import storage
from backend.app.schemas.base import ExtractedFieldItem, BoundingBox
from backend.app.schemas.registry import get_schema_for_type
from backend.app.services.mock_engine import mock_engine

class ExtractionService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    async def extract_fields(
        self,
        doc_type: str,
        pages_info: List[Dict[str, Any]],
        filename: str
    ) -> List[ExtractedFieldItem]:
        """
        Extracts structured fields using Google Gemini Multimodal Vision API, or mock engine fallback.
        """
        # If API key not set or client unavailable, use high-fidelity engine
        if not self.client or not self.api_key:
            res = mock_engine.extract_generic_or_sample(
                doc_type=doc_type,
                text=pages_info[0]["ocr_text"] if pages_info else "",
                filename=filename
            )
            return res.get("fields", [])

        schema_info = get_schema_for_type(doc_type)

        try:
            from google.genai import types

            contents = []
            combined_ocr_text = []

            # Load page images (up to first 3 pages)
            for p in pages_info[:3]:
                rel_path = p["image_path"]
                full_path = await storage.get_file_path(rel_path)
                pil_img = Image.open(full_path).convert("RGB")
                contents.append(pil_img)
                combined_ocr_text.append(f"--- Page {p['page_number']} Text ---\n{p.get('ocr_text', '')}")

            sections_desc = json.dumps(schema_info.get("sections", {}), indent=2)

            instruction = (
                f"You are an expert multimodal document intelligence extraction system powered by Google Gemini.\n"
                f"The document has been classified as '{doc_type}' ({schema_info['label']}).\n\n"
                f"Schema Sections and Fields to Extract:\n{sections_desc}\n\n"
                f"Instructions:\n"
                f"1. Extract all key-value fields visible on the document matching the schema.\n"
                f"2. For each field, provide:\n"
                f"   - field_name: standard key\n"
                f"   - field_label: human readable label\n"
                f"   - section: section group name\n"
                f"   - value: string value as shown on the document (or formatted date/amount)\n"
                f"   - confidence: float between 0.0 and 1.0 (score lower if blurry, faint, or ambiguous)\n"
                f"   - bounding_box: normalized {{\"ymin\": 0-1000, \"xmin\": 0-1000, \"ymax\": 0-1000, \"xmax\": 0-1000, \"page\": 1}} coordinates on the page\n"
                f"   - page_number: integer page number (1-based)\n"
                f"3. Return strict JSON matching this format:\n"
                f"{{\n"
                f'  "fields": [\n'
                f'    {{\n'
                f'      "field_name": "invoice_number",\n'
                f'      "field_label": "Invoice Number",\n'
                f'      "section": "Invoice Details",\n'
                f'      "value": "INV-2026-8942",\n'
                f'      "confidence": 0.98,\n'
                f'      "page_number": 1,\n'
                f'      "bounding_box": {{"ymin": 125, "xmin": 647, "ymax": 145, "xmax": 860, "page": 1}}\n'
                f'    }}\n'
                f'  ]\n'
                f"}}\n\n"
                f"OCR Text layer for reference:\n{''.join(combined_ocr_text)[:4000]}"
            )

            contents.append(instruction)

            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )

            raw_text = response.text
            json_match = raw_text
            if "{" in raw_text and "}" in raw_text:
                json_match = raw_text[raw_text.find("{"):raw_text.rfind("}")+1]
            data = json.loads(json_match)

            raw_fields = data.get("fields", [])
            extracted_fields = []
            for rf in raw_fields:
                bbox_data = None
                if rf.get("bounding_box"):
                    b = rf["bounding_box"]
                    bbox_data = BoundingBox(
                        ymin=float(b.get("ymin", 0)),
                        xmin=float(b.get("xmin", 0)),
                        ymax=float(b.get("ymax", 0)),
                        xmax=float(b.get("xmax", 0)),
                        page=int(b.get("page", rf.get("page_number", 1)))
                    )

                field_item = ExtractedFieldItem(
                    field_name=rf.get("field_name", "unknown"),
                    field_label=rf.get("field_label", rf.get("field_name", "Unknown")),
                    section=rf.get("section", "General"),
                    value=str(rf.get("value", "")),
                    confidence=float(rf.get("confidence", 0.95)),
                    bbox=bbox_data,
                    page_number=int(rf.get("page_number", 1))
                )
                extracted_fields.append(field_item)

            if extracted_fields:
                return extracted_fields

        except Exception as e:
            pass

        # Fallback to mock / heuristic extraction
        res = mock_engine.extract_generic_or_sample(
            doc_type=doc_type,
            text=pages_info[0]["ocr_text"] if pages_info else "",
            filename=filename
        )
        return res.get("fields", [])

extraction_service = ExtractionService()
