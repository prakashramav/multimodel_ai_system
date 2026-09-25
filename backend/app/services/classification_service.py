import json
from pathlib import Path
from typing import Optional
from PIL import Image
from backend.app.core.config import settings
from backend.app.core.storage import storage
from backend.app.schemas.base import ClassificationOutput
from backend.app.services.mock_engine import mock_engine

class ClassificationService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    async def classify_document(
        self,
        first_page_rel_path: str,
        extracted_text: str,
        filename: str
    ) -> ClassificationOutput:
        """
        Classifies document type using Google Gemini Vision API, or fallback heuristic engine.
        Taxonomy: invoice, resume, receipt, contract, form, other
        """
        if not self.client or not self.api_key:
            # High-fidelity heuristic / fixture classification
            return mock_engine.classify_heuristically(extracted_text, filename)

        try:
            from google.genai import types

            full_img_path = await storage.get_file_path(first_page_rel_path)
            pil_img = Image.open(full_img_path).convert("RGB")

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

            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[pil_img, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )

            raw_text = response.text
            # Extract JSON block
            json_match = raw_text
            if "{" in raw_text and "}" in raw_text:
                json_match = raw_text[raw_text.find("{"):raw_text.rfind("}")+1]
            data = json.loads(json_match)

            return ClassificationOutput(
                document_type=data.get("document_type", "invoice"),
                confidence=float(data.get("confidence", 0.95)),
                reasoning=data.get("reasoning", "Classified via Google Gemini Vision")
            )
        except Exception as e:
            # Graceful fallback on API error or rate limit
            return mock_engine.classify_heuristically(extracted_text, filename)

classification_service = ClassificationService()
