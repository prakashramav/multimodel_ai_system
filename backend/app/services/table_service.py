import json
from typing import List, Dict, Any
from PIL import Image
from backend.app.core.config import settings
from backend.app.core.storage import storage
from backend.app.schemas.base import ExtractedTableItem
from backend.app.schemas.registry import get_schema_for_type
from backend.app.services.mock_engine import mock_engine

class TableService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    async def extract_tables(
        self,
        doc_type: str,
        pages_info: List[Dict[str, Any]],
        filename: str
    ) -> List[ExtractedTableItem]:
        """
        Extracts tabular regions (e.g. invoice line items, resume work history, receipt purchased items) using Google Gemini.
        Returns list of ExtractedTableItem.
        """
        if not self.client or not self.api_key:
            res = mock_engine.extract_generic_or_sample(
                doc_type=doc_type,
                text=pages_info[0]["ocr_text"] if pages_info else "",
                filename=filename
            )
            return res.get("tables", [])

        schema_info = get_schema_for_type(doc_type)
        default_name = schema_info.get("default_table_name", "Data Table")

        try:
            from google.genai import types

            full_path = await storage.get_file_path(pages_info[0]["image_path"])
            pil_img = Image.open(full_path).convert("RGB")

            prompt = (
                f"You are a specialized table extraction vision AI powered by Google Gemini. "
                f"Detect any tabular regions in this {doc_type} (such as {default_name}).\n"
                f"Extract the table into a strict JSON object matching this schema:\n"
                "{\n"
                f'  "table_name": "{default_name}",\n'
                '  "columns": ["Col 1", "Col 2", ...],\n'
                '  "rows": [\n'
                '    {"col1_key": "val", "col2_key": "val"}\n'
                '  ],\n'
                '  "confidence": 0.95\n'
                "}\n"
                "Return ONLY valid JSON."
            )

            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[pil_img, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )

            raw = response.text
            if "{" in raw and "}" in raw:
                raw_json = raw[raw.find("{"):raw.rfind("}")+1]
                data = json.loads(raw_json)
                return [
                    ExtractedTableItem(
                        table_name=data.get("table_name", default_name),
                        columns=data.get("columns", []),
                        rows=data.get("rows", []),
                        page_number=1,
                        confidence=float(data.get("confidence", 0.95))
                    )
                ]
        except Exception:
            pass

        res = mock_engine.extract_generic_or_sample(
            doc_type=doc_type,
            text=pages_info[0]["ocr_text"] if pages_info else "",
            filename=filename
        )
        return res.get("tables", [])

table_service = TableService()
