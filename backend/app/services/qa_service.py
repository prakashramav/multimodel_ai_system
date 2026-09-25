import json
from typing import List, Dict, Any, Tuple
from backend.app.core.config import settings

class QAService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    async def answer_question(
        self,
        question: str,
        document_dict: Dict[str, Any],
        fields: List[Dict[str, Any]],
        tables: List[Dict[str, Any]],
        pages: List[Dict[str, Any]]
    ) -> Tuple[str, List[str]]:
        """
        Answers a free-form question grounded strictly in document content using Google Gemini.
        Returns: (answer_string, list_of_grounded_sources)
        """
        # Build context
        context_parts = []
        context_parts.append(f"DOCUMENT TYPE: {document_dict.get('type', 'Unknown').upper()}")
        context_parts.append(f"FILENAME: {document_dict.get('filename')}")

        context_parts.append("\n--- EXTRACTED STRUCTURED FIELDS ---")
        for f in fields:
            context_parts.append(f"- {f.get('field_label', f.get('field_name'))} ({f.get('section')}): {f.get('value')}")

        if tables:
            context_parts.append("\n--- EXTRACTED TABLES ---")
            for t in tables:
                context_parts.append(f"Table '{t.get('table_name')}':")
                cols = t.get("columns", [])
                context_parts.append(f"Columns: {', '.join(cols)}")
                for idx, row in enumerate(t.get("rows", [])):
                    row_str = ", ".join([f"{k}: {v}" for k, v in row.items()])
                    context_parts.append(f"  Row {idx+1}: {row_str}")

        context_parts.append("\n--- FULL PAGE OCR TEXT ---")
        for p in pages:
            context_parts.append(f"[Page {p.get('page_number')}]:\n{p.get('ocr_text', '')}\n")

        full_context = "\n".join(context_parts)

        # If Gemini client is available:
        if self.client and self.api_key:
            prompt = (
                "You are a strict, grounded document question-answering assistant powered by Google Gemini.\n"
                "Answer the user's question relying ONLY on the provided document context below.\n"
                "RULES:\n"
                "1. If the information is not present or cannot be determined from the document, say explicitly: "
                "'This information is not stated in the provided document.' Do NOT speculate or infer.\n"
                "2. Provide a concise, clear answer.\n"
                "3. At the end of your answer, list exact citations/sources from the document under a line starting with 'Sources: '.\n\n"
                f"DOCUMENT CONTEXT:\n{full_context}\n\n"
                f"QUESTION: {question}"
            )

            try:
                from google.genai import types
                response = self.client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1
                    )
                )
                ans = response.text
                sources = []
                if "Sources:" in ans:
                    src_part = ans.split("Sources:")[1]
                    sources = [s.strip(" -*") for s in src_part.split("\n") if s.strip()]
                else:
                    sources = [document_dict.get("filename", "Document Context")]
                return ans, sources
            except Exception:
                pass

        # Intelligent local grounded QA fallback engine:
        q_lower = question.lower()
        matched_sources = []
        matched_answers = []

        # 1. Search in structured fields
        for f in fields:
            label = (f.get("field_label") or "").lower()
            name = (f.get("field_name") or "").lower()
            val = str(f.get("value") or "")
            
            # Direct match check
            if any(term in q_lower for term in ["due date", "when is it due", "payment due"]) and "due" in name:
                return f"The payment due date is **{val}**.", [f"Field: {f.get('field_label')}"]
            elif any(term in q_lower for term in ["invoice number", "invoice #", "inv #"]) and "invoice_number" in name:
                return f"The invoice number is **{val}**.", [f"Field: {f.get('field_label')}"]
            elif any(term in q_lower for term in ["total", "amount due", "how much"]) and "total" in name:
                return f"The total amount due is **{val}**.", [f"Field: {f.get('field_label')}"]
            elif any(term in q_lower for term in ["vendor", "who issued", "who sent", "company"]) and "vendor_name" in name:
                return f"The vendor issuing this invoice is **{val}**.", [f"Field: {f.get('field_label')}"]
            elif any(term in q_lower for term in ["customer", "bill to", "client", "who is billed"]) and "customer_name" in name:
                return f"The billed customer is **{val}**.", [f"Field: {f.get('field_label')}"]
            elif any(term in q_lower for term in ["gpa", "grade", "honors"]) and "gpa" in name:
                return f"The candidate's GPA/Honors is **{val}**.", [f"Field: {f.get('field_label')}"]
            elif any(term in q_lower for term in ["degree", "education", "university", "college"]) and ("degree" in name or "institution" in name):
                matched_answers.append(f"{f.get('field_label')}: {val}")
                matched_sources.append(f"Field: {f.get('field_label')}")
            elif any(term in q_lower for term in ["skills", "technologies", "tech stack"]) and "skills" in name:
                return f"The key skills listed are: **{val}**.", [f"Field: {f.get('field_label')}"]
            elif any(term in q_lower for term in ["receipt", "merchant", "store"]) and "merchant_name" in name:
                return f"The merchant is **{val}**.", [f"Field: {f.get('field_label')}"]
            elif any(term in q_lower for term in ["auto-renewal", "auto renewal", "renew"]) and "renewal" in name:
                return f"Auto-renewal terms: **{val}**.", [f"Field: {f.get('field_label')}"]

        if matched_answers:
            return "\n".join(matched_answers), matched_sources

        # 2. Check tables (e.g. line items or experience)
        for t in tables:
            tname = t.get("table_name", "")
            for row in t.get("rows", []):
                for col, cell in row.items():
                    if any(term in q_lower for term in str(cell).lower().split() if len(term) > 3):
                        return f"From '{tname}': Found item details: {json.dumps(row, indent=2)}", [f"Table: {tname}"]

        # 3. Text search
        for p in pages:
            lines = (p.get("ocr_text") or "").split("\n")
            for line in lines:
                if any(word in line.lower() for word in q_lower.split() if len(word) > 4):
                    return f"Found in document (Page {p.get('page_number')}):\n\n> {line.strip()}", [f"Page {p.get('page_number')} Text"]

        return "This information is not stated in the provided document.", ["Document Verification"]

qa_service = QAService()
