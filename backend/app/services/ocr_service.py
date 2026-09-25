import os
import io
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PIL import Image
import pypdfium2 as pdfium
import pypdf
from backend.app.core.config import settings
from backend.app.core.storage import storage

class OCRService:
    def __init__(self):
        self.tesseract_available = False
        if settings.TESSERACT_CMD:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
            self.tesseract_available = True
        else:
            try:
                import pytesseract
                # Test call
                pytesseract.get_tesseract_version()
                self.tesseract_available = True
            except Exception:
                self.tesseract_available = False

    async def rasterize_and_extract(
        self,
        file_path: str,
        doc_id: str,
        mime_type: str = "application/pdf"
    ) -> List[Dict[str, Any]]:
        """
        Converts document (PDF or image) into page images and extracts text layer.
        Returns a list of page dicts:
        [{
           "page_number": 1,
           "image_path": "pages/...",
           "width": int,
           "height": int,
           "ocr_text": str,
           "ocr_data": dict
        }]
        """
        results = []
        is_pdf = mime_type == "application/pdf" or file_path.lower().endswith(".pdf")

        if is_pdf:
            pdf_doc = pdfium.PdfDocument(file_path)
            num_pages = len(pdf_doc)

            # Also open with pypdf for text layer extraction
            pypdf_reader = None
            try:
                pypdf_reader = pypdf.PdfReader(file_path)
            except Exception:
                pass

            for page_idx in range(num_pages):
                page_num = page_idx + 1
                page = pdf_doc.get_page(page_idx)
                
                # Render at 2x scale (~144-150 DPI) for crisp text & vision LLM clarity
                pil_img = page.render(scale=2).to_pil()
                w, h = pil_img.size

                # Save page image to storage
                rel_img_path = f"pages/{doc_id}_p{page_num}.png"
                img_byte_arr = io.BytesIO()
                pil_img.save(img_byte_arr, format="PNG", optimize=True)
                img_byte_arr.seek(0)
                await storage.save_file(img_byte_arr.getvalue(), rel_img_path)

                # Extract text layer
                extracted_text = ""
                if pypdf_reader and page_idx < len(pypdf_reader.pages):
                    try:
                        extracted_text = pypdf_reader.pages[page_idx].extract_text() or ""
                    except Exception:
                        pass

                # If text layer is sparse/empty and tesseract is available, run OCR
                ocr_words = []
                if (not extracted_text.strip() or len(extracted_text) < 30) and self.tesseract_available:
                    try:
                        import pytesseract
                        ocr_data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
                        extracted_text = pytesseract.image_to_string(pil_img)
                        # Extract word bounding boxes
                        for i in range(len(ocr_data["text"])):
                            txt = ocr_data["text"][i].strip()
                            if txt:
                                ocr_words.append({
                                    "text": txt,
                                    "conf": float(ocr_data["conf"][i]),
                                    "box": [
                                        ocr_data["top"][i] / h * 1000,
                                        ocr_data["left"][i] / w * 1000,
                                        (ocr_data["top"][i] + ocr_data["height"][i]) / h * 1000,
                                        (ocr_data["left"][i] + ocr_data["width"][i]) / w * 1000,
                                    ]
                                })
                    except Exception:
                        pass

                results.append({
                    "page_number": page_num,
                    "image_path": rel_img_path,
                    "width": w,
                    "height": h,
                    "ocr_text": extracted_text.strip(),
                    "ocr_data": {"words": ocr_words}
                })

        else:
            # Document is an image (PNG, JPG, TIFF, etc.)
            with Image.open(file_path) as img:
                pil_img = img.convert("RGB")
                w, h = pil_img.size

                rel_img_path = f"pages/{doc_id}_p1.png"
                img_byte_arr = io.BytesIO()
                pil_img.save(img_byte_arr, format="PNG", optimize=True)
                img_byte_arr.seek(0)
                await storage.save_file(img_byte_arr.getvalue(), rel_img_path)

                extracted_text = ""
                ocr_words = []
                if self.tesseract_available:
                    try:
                        import pytesseract
                        extracted_text = pytesseract.image_to_string(pil_img)
                    except Exception:
                        pass

                results.append({
                    "page_number": 1,
                    "image_path": rel_img_path,
                    "width": w,
                    "height": h,
                    "ocr_text": extracted_text.strip(),
                    "ocr_data": {"words": ocr_words}
                })

        return results

ocr_service = OCRService()
