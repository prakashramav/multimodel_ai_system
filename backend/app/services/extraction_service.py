import base64
import json
from typing import List, Dict, Any, Tuple
from backend.app.core.config import settings
from backend.app.core.storage import storage
from backend.app.schemas.base import ExtractedFieldItem, BoundingBox
from backend.app.schemas.registry import get_schema_for_type
from backend.app.services.mock_engine import mock_engine

class ExtractionService:
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.client = None
        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except Exception:
                self.client = None

    async def extract_fields(
        self,
        doc_type: str,
        pages_info: List[Dict[str, Any]],
        filename: str
    ) -> List[ExtractedFieldItem]:
        """
        Extracts structured fields using Claude Vision tool-use, or mock engine fallback.
        """
        # If API key not set or client unavailable, use high fidelity engine
        if not self.client or not self.api_key:
            res = mock_engine.extract_generic_or_sample(
                doc_type=doc_type,
                text=pages_info[0]["ocr_text"] if pages_info else "",
                filename=filename
            )
            return res.get("fields", [])

        schema_info = get_schema_for_type(doc_type)
        tool_spec = schema_info["tool_spec"]

        try:
            # Build multimodal content array (up to first 3 pages)
            content_blocks = []
            combined_ocr_text = []

            for p in pages_info[:3]:
                rel_path = p["image_path"]
                full_path = await storage.get_file_path(rel_path)
                with open(full_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                
                content_blocks.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": b64
                    }
                })
                combined_ocr_text.append(f"--- Page {p['page_number']} Text ---\n{p.get('ocr_text', '')}")

            instruction = (
                f"You are an expert multimodal document intelligence extraction system.\n"
                f"The document has been classified as '{doc_type}' ({schema_info['label']}).\n\n"
                f"Instructions:\n"
                f"1. Extract all structured fields according to the schema sections for {doc_type}.\n"
                f"2. For each field, provide:\n"
                f"   - field_name: standard key\n"
                f"   - field_label: human readable label\n"
                f"   - section: section group\n"
                f"   - value: string value as shown on the document (or normalized date/amount)\n"
                f"   - confidence: float between 0.0 and 1.0 (score lower if blurry, faint, or ambiguous)\n"
                f"   - bounding_box: normalized [ymin, xmin, ymax, xmax] (0 to 1000 scale) bounding box on the page\n"
                f"   - page_number: integer page number (1-based)\n"
                f"3. Call the provided tool `{tool_spec['name']}` to return the structured data.\n\n"
                f"OCR Text layer for reference:\n{''.join(combined_ocr_text)[:4000]}"
            )

            content_blocks.append({"type": "text", "text": instruction})

            response = await self.client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=2500,
                tools=[tool_spec],
                tool_choice={"type": "tool", "name": tool_spec["name"]},
                messages=[{"role": "user", "content": content_blocks}]
            )

            # Parse tool call from response
            extracted_fields = []
            for block in response.content:
                if block.type == "tool_use" and block.name == tool_spec["name"]:
                    tool_input = block.input
                    raw_fields = tool_input.get("fields", [])
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
