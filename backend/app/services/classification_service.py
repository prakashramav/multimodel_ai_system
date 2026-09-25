import base64
import json
from pathlib import Path
from typing import Optional
from backend.app.core.config import settings
from backend.app.core.storage import storage
from backend.app.schemas.base import ClassificationOutput
from backend.app.services.mock_engine import mock_engine

class ClassificationService:
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.client = None
        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except Exception:
                self.client = None

    async def classify_document(
        self,
        first_page_rel_path: str,
        extracted_text: str,
        filename: str
    ) -> ClassificationOutput:
        """
        Classifies document type using Claude Vision API, or fallback heuristic engine.
        Taxonomy: invoice, resume, receipt, contract, form, other
        """
        if not self.client or not self.api_key:
            # High-fidelity heuristic / fixture classification
            return mock_engine.classify_heuristically(extracted_text, filename)

        try:
            full_img_path = await storage.get_file_path(first_page_rel_path)
            with open(full_img_path, "rb") as img_file:
                b64_image = base64.b64encode(img_file.read()).decode("utf-8")

            prompt = (
                "You are an expert document classification AI. Analyze the image and text of the first page of this document.\n"
                "Classify it into exactly one of these document types:\n"
                "- invoice\n"
                "- resume\n"
                "- receipt\n"
                "- contract\n"
                "- form\n"
                "- other\n\n"
                f"Filename: {filename}\n"
                f"OCR Text sample: {extracted_text[:1500]}\n\n"
                "Return a valid JSON object matching this schema:\n"
                "{\n"
                '  "document_type": "invoice|resume|receipt|contract|form|other",\n'
                '  "confidence": 0.95,\n'
                '  "reasoning": "Brief explanation of layout, header, and visual cues"\n'
                "}"
            )

            response = await self.client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=400,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": b64_image
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

            raw_text = response.content[0].text
            # Extract JSON block
            json_match = raw_text
            if "{" in raw_text and "}" in raw_text:
                json_match = raw_text[raw_text.find("{"):raw_text.rfind("}")+1]
            data = json.loads(json_match)
            return ClassificationOutput(
                document_type=data.get("document_type", "invoice"),
                confidence=float(data.get("confidence", 0.9)),
                reasoning=data.get("reasoning", "Classified via Claude Vision")
            )
        except Exception as e:
            # Graceful fallback on API error or rate limit
            return mock_engine.classify_heuristically(extracted_text, filename)

classification_service = ClassificationService()
