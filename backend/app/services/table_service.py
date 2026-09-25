import base64
import json
from typing import List, Dict, Any
from backend.app.core.config import settings
from backend.app.core.storage import storage
from backend.app.schemas.base import ExtractedTableItem
from backend.app.schemas.registry import get_schema_for_type
from backend.app.services.mock_engine import mock_engine

class TableService:
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.client = None
        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except Exception:
                self.client = None

    async def extract_tables(
        self,
        doc_type: str,
        pages_info: List[Dict[str, Any]],
        filename: str
    ) -> List[ExtractedTableItem]:
        """
        Extracts tabular regions (e.g. invoice line items, resume work history, receipt purchased items).
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
            # We can prompt Claude to extract tables as JSON
            full_path = await storage.get_file_path(pages_info[0]["image_path"])
            with open(full_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")

            prompt = (
                f"You are a specialized table extraction model. Detect any tabular regions in this {doc_type} "
                f"(such as {default_name}).\n"
                f"Extract the table into a strict JSON object:\n"
                "{\n"
                f'  "table_name": "{default_name}",\n'
                '  "columns": ["Col 1", "Col 2", ...],\n'
                '  "rows": [\n'
                '    {"col1_key": "val", "col2_key": "val"}\n'
                '  ],\n'
                '  "confidence": 0.95\n'
                "}\n"
                "Return ONLY this JSON object."
            )

            response = await self.client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": b64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )

            raw = response.content[0].text
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
