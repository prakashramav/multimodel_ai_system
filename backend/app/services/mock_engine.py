import re
from typing import Dict, Any, List
from backend.app.schemas.base import ClassificationOutput, ExtractedFieldItem, ExtractedTableItem, BoundingBox

class MockEngine:
    """High-fidelity fixture and heuristic extraction engine for demo mode / testing without API keys."""

    def classify_heuristically(self, text: str, filename: str) -> ClassificationOutput:
        lower_text = (text + " " + filename).lower()
        
        # Scoring logic
        invoice_score = sum(1 for kw in ["invoice", "bill to", "due date", "subtotal", "tax id", "amount due", "vendor", "po number"] if kw in lower_text)
        resume_score = sum(1 for kw in ["resume", "curriculum vitae", "education", "experience", "skills", "bachelor", "master", "gpa", "work history"] if kw in lower_text)
        receipt_score = sum(1 for kw in ["receipt", "cashier", "subtotal", "tax", "tip", "visa", "card", "paid", "store", "terminal", "order:"] if kw in lower_text)
        contract_score = sum(1 for kw in ["agreement", "contract", "parties", "hereby", "jurisdiction", "terms and conditions", "effective date", "governing law"] if kw in lower_text)

        scores = [
            ("invoice", invoice_score),
            ("resume", resume_score),
            ("receipt", receipt_score),
            ("contract", contract_score)
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        best_type, best_score = scores[0]

        if best_score >= 2:
            conf = min(0.98, 0.70 + (best_score * 0.05))
            reasoning = f"Detected characteristic {best_type} vocabulary and structural layout markers."
            return ClassificationOutput(document_type=best_type, confidence=conf, reasoning=reasoning)
        
        # Check filename hints
        if "invoice" in lower_text:
            return ClassificationOutput(document_type="invoice", confidence=0.92, reasoning="Filename and header indicate commercial invoice.")
        elif "resume" in lower_text or "cv" in lower_text:
            return ClassificationOutput(document_type="resume", confidence=0.94, reasoning="Filename and structure indicate professional resume.")
        elif "receipt" in lower_text:
            return ClassificationOutput(document_type="receipt", confidence=0.93, reasoning="Document dimensions and keywords match store receipt.")

        return ClassificationOutput(document_type="invoice", confidence=0.82, reasoning="Defaulted to invoice schema based on standard tabular structure.")

    def get_sample_invoice_extraction(self) -> Dict[str, Any]:
        fields = [
            # Vendor Details
            ExtractedFieldItem(
                field_name="vendor_name",
                field_label="Vendor Name",
                section="Vendor Details",
                value="Vertex Technologies Inc.",
                confidence=0.99,
                bbox=BoundingBox(ymin=125, xmin=47, ymax=145, xmax=280, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="vendor_address",
                field_label="Vendor Address",
                section="Vendor Details",
                value="450 Mission Street, Suite 1200, San Francisco, CA 94105",
                confidence=0.96,
                bbox=BoundingBox(ymin=148, xmin=47, ymax=185, xmax=340, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="vendor_tax_id",
                field_label="Vendor Tax ID / VAT",
                section="Vendor Details",
                value="US-94-3829104",
                confidence=0.94,
                bbox=BoundingBox(ymin=188, xmin=47, ymax=208, xmax=220, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="vendor_email",
                field_label="Vendor Email",
                section="Vendor Details",
                value="billing@vertexcloud.io",
                confidence=0.98,
                bbox=BoundingBox(ymin=210, xmin=47, ymax=228, xmax=205, page=1),
                page_number=1
            ),
            
            # Invoice Details
            ExtractedFieldItem(
                field_name="invoice_number",
                field_label="Invoice Number",
                section="Invoice Details",
                value="INV-2026-8942",
                confidence=0.99,
                bbox=BoundingBox(ymin=125, xmin=647, ymax=145, xmax=860, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="invoice_date",
                field_label="Invoice Date",
                section="Invoice Details",
                value="2026-03-15",
                confidence=0.97,
                bbox=BoundingBox(ymin=148, xmin=647, ymax=168, xmax=830, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="due_date",
                field_label="Payment Due Date",
                section="Invoice Details",
                value="2026-04-14",
                confidence=0.96,
                bbox=BoundingBox(ymin=170, xmin=647, ymax=190, xmax=830, page=1),
                page_number=1
            ),
            # Intentional low confidence field to exercise review queue!
            ExtractedFieldItem(
                field_name="purchase_order_number",
                field_label="PO Number",
                section="Invoice Details",
                value="PO-9821-X",
                confidence=0.64,  # Below threshold (0.75)! Flags for human review
                bbox=BoundingBox(ymin=192, xmin=647, ymax=212, xmax=820, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="payment_terms",
                field_label="Payment Terms",
                section="Invoice Details",
                value="Net 30 Days",
                confidence=0.91,
                bbox=BoundingBox(ymin=214, xmin=647, ymax=234, xmax=820, page=1),
                page_number=1
            ),

            # Customer Details
            ExtractedFieldItem(
                field_name="customer_name",
                field_label="Customer / Bill To",
                section="Customer Details",
                value="Horizon Logistics Global Ltd.",
                confidence=0.98,
                bbox=BoundingBox(ymin=245, xmin=55, ymax=268, xmax=340, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="customer_address",
                field_label="Billing Address",
                section="Customer Details",
                value="742 Evergreen Terrace, Floor 4, Seattle, WA 98101",
                confidence=0.95,
                bbox=BoundingBox(ymin=270, xmin=55, ymax=290, xmax=470, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="customer_email",
                field_label="Customer Email",
                section="Customer Details",
                value="ap@horizonlogistics.com",
                confidence=0.97,
                bbox=BoundingBox(ymin=270, xmin=647, ymax=290, xmax=850, page=1),
                page_number=1
            ),

            # Totals & Financials
            ExtractedFieldItem(
                field_name="currency",
                field_label="Currency",
                section="Totals & Financials",
                value="USD",
                confidence=0.99,
                bbox=BoundingBox(ymin=590, xmin=647, ymax=620, xmax=850, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="subtotal",
                field_label="Subtotal",
                section="Totals & Financials",
                value="$15,100.00",
                confidence=0.98,
                bbox=BoundingBox(ymin=500, xmin=820, ymax=520, xmax=930, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="discount_amount",
                field_label="Discount",
                section="Totals & Financials",
                value="$755.00",
                confidence=0.93,
                bbox=BoundingBox(ymin=522, xmin=820, ymax=542, xmax=930, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="tax_amount",
                field_label="Tax Amount",
                section="Totals & Financials",
                value="$1,219.33",
                confidence=0.94,
                bbox=BoundingBox(ymin=545, xmin=820, ymax=565, xmax=930, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="total_amount",
                field_label="Total Amount Due",
                section="Totals & Financials",
                value="$15,564.33",
                confidence=0.99,
                bbox=BoundingBox(ymin=590, xmin=820, ymax=615, xmax=940, page=1),
                page_number=1
            ),
        ]

        table = ExtractedTableItem(
            table_name="Line Items",
            columns=["Item Description", "Qty", "Unit Price", "Tax", "Total Amount"],
            rows=[
                {
                    "item_description": "Dedicated GPU Cluster (H100 NVLink) - March 2026",
                    "quantity": "2",
                    "unit_price": "$4,200.00",
                    "tax_rate": "8.5%",
                    "total_amount": "$8,400.00"
                },
                {
                    "item_description": "Managed Kubernetes Control Plane Enterprise tier",
                    "quantity": "1",
                    "unit_price": "$1,250.00",
                    "tax_rate": "8.5%",
                    "total_amount": "$1,250.00"
                },
                {
                    "item_description": "Distributed S3-Compatible Storage (50 TB Tier)",
                    "quantity": "50",
                    "unit_price": "$24.00",
                    "tax_rate": "8.5%",
                    "total_amount": "$1,200.00"
                },
                {
                    "item_description": "Premium 24/7 SLA Technical Support & Dedicated TAM",
                    "quantity": "1",
                    "unit_price": "$750.00",
                    "tax_rate": "0.0%",
                    "total_amount": "$750.00"
                },
                {
                    "item_description": "Custom Document Parsing Neural Pipeline Integration",
                    "quantity": "1",
                    "unit_price": "$3,500.00",
                    "tax_rate": "8.5%",
                    "total_amount": "$3,500.00"
                }
            ],
            page_number=1,
            confidence=0.98
        )

        return {"fields": fields, "tables": [table]}

    def get_sample_resume_extraction(self) -> Dict[str, Any]:
        fields = [
            ExtractedFieldItem(
                field_name="full_name",
                field_label="Full Name",
                section="Personal Details",
                value="Alex Morgan",
                confidence=0.99,
                bbox=BoundingBox(ymin=20, xmin=47, ymax=45, xmax=220, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="email",
                field_label="Email Address",
                section="Personal Details",
                value="alex.morgan.ai@example.com",
                confidence=0.98,
                bbox=BoundingBox(ymin=65, xmin=47, ymax=85, xmax=270, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="phone",
                field_label="Phone Number",
                section="Personal Details",
                value="+1 (650) 492-8172",
                confidence=0.96,
                bbox=BoundingBox(ymin=65, xmin=280, ymax=85, xmax=410, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="location",
                field_label="Current Location",
                section="Personal Details",
                value="San Francisco, CA",
                confidence=0.97,
                bbox=BoundingBox(ymin=65, xmin=420, ymax=85, xmax=540, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="github_or_portfolio",
                field_label="Portfolio / GitHub",
                section="Personal Details",
                value="github.com/alexmorgan-ai",
                confidence=0.95,
                bbox=BoundingBox(ymin=65, xmin=550, ymax=85, xmax=720, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="current_title",
                field_label="Current / Target Title",
                section="Professional Profile",
                value="Staff AI Systems Engineer & Full-Stack Architect",
                confidence=0.98,
                bbox=BoundingBox(ymin=45, xmin=47, ymax=65, xmax=450, page=1),
                page_number=1
            ),
            # Slightly lower confidence on calculated years of experience
            ExtractedFieldItem(
                field_name="years_of_experience",
                field_label="Total Years Experience",
                section="Professional Profile",
                value="8+ years",
                confidence=0.68,  # Below threshold (0.75)! Triggers human review
                bbox=BoundingBox(ymin=135, xmin=47, ymax=160, xmax=200, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="primary_skills",
                field_label="Primary Skills",
                section="Professional Profile",
                value="Python, TypeScript, FastAPI, Next.js, PyTorch, SQLAlchemy, React, Go",
                confidence=0.97,
                bbox=BoundingBox(ymin=190, xmin=47, ymax=215, xmax=750, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="tools_frameworks",
                field_label="Tools & Frameworks",
                section="Professional Profile",
                value="Claude Vision, OpenAI, Transformers, LangChain, DocVQA, RAG, AWS, Docker, Kubernetes",
                confidence=0.95,
                bbox=BoundingBox(ymin=215, xmin=47, ymax=240, xmax=800, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="highest_degree",
                field_label="Highest Degree",
                section="Education Summary",
                value="Master of Science in Computer Science",
                confidence=0.99,
                bbox=BoundingBox(ymin=650, xmin=47, ymax=675, xmax=600, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="institution",
                field_label="Institution",
                section="Education Summary",
                value="University of Washington, Seattle",
                confidence=0.98,
                bbox=BoundingBox(ymin=675, xmin=47, ymax=700, xmax=420, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="gpa_or_honors",
                field_label="GPA / Honors",
                section="Education Summary",
                value="3.92 / 4.0",
                confidence=0.95,
                bbox=BoundingBox(ymin=675, xmin=430, ymax=700, xmax=550, page=1),
                page_number=1
            )
        ]

        table = ExtractedTableItem(
            table_name="Work History",
            columns=["Role", "Company", "Dates", "Location", "Highlights"],
            rows=[
                {
                    "job_title": "Staff AI Platform Engineer",
                    "company": "ScaleAI Technologies",
                    "dates": "2023 - Present",
                    "location": "San Francisco, CA",
                    "highlights": "Spearheaded multimodal doc intelligence architecture; reduced latency 45%."
                },
                {
                    "job_title": "Senior Backend Engineer",
                    "company": "NeuralDocs Inc.",
                    "dates": "2020 - 2023",
                    "location": "Seattle, WA (Remote)",
                    "highlights": "Built high-concurrency OCR microservices handling 250+ req/sec with FastAPI."
                },
                {
                    "job_title": "Software Engineer",
                    "company": "CloudMatrix Solutions",
                    "dates": "2018 - 2020",
                    "location": "Austin, TX",
                    "highlights": "Designed REST APIs and automated AWS infrastructure with Terraform."
                }
            ],
            page_number=1,
            confidence=0.97
        )

        return {"fields": fields, "tables": [table]}

    def get_sample_receipt_extraction(self) -> Dict[str, Any]:
        fields = [
            ExtractedFieldItem(
                field_name="merchant_name",
                field_label="Merchant / Store Name",
                section="Merchant Details",
                value="Blue Bottle Coffee",
                confidence=0.99,
                bbox=BoundingBox(ymin=35, xmin=200, ymax=60, xmax=800, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="merchant_address",
                field_label="Store Address",
                section="Merchant Details",
                value="315 Linden St, San Francisco, CA",
                confidence=0.97,
                bbox=BoundingBox(ymin=60, xmin=200, ymax=85, xmax=800, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="tax_id",
                field_label="Tax / VAT ID",
                section="Merchant Details",
                value="CA-94829103-01",
                confidence=0.93,
                bbox=BoundingBox(ymin=95, xmin=200, ymax=115, xmax=800, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="receipt_number",
                field_label="Receipt / Check #",
                section="Transaction Details",
                value="RCP-839201",
                confidence=0.98,
                bbox=BoundingBox(ymin=150, xmin=50, ymax=170, xmax=350, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="transaction_date",
                field_label="Date",
                section="Transaction Details",
                value="2026-03-24",
                confidence=0.98,
                bbox=BoundingBox(ymin=170, xmin=50, ymax=190, xmax=350, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="transaction_time",
                field_label="Time",
                section="Transaction Details",
                value="10:14 AM",
                confidence=0.96,
                bbox=BoundingBox(ymin=170, xmin=600, ymax=190, xmax=850, page=1),
                page_number=1
            ),
            # Low-confidence cashier / terminal ID
            ExtractedFieldItem(
                field_name="cashier_id",
                field_label="Server / Cashier",
                section="Transaction Details",
                value="Marcus K.",
                confidence=0.71,  # Below threshold (0.75)! Triggers review
                bbox=BoundingBox(ymin=190, xmin=50, ymax=210, xmax=350, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="payment_method",
                field_label="Payment Method",
                section="Transaction Details",
                value="Visa Contactless",
                confidence=0.98,
                bbox=BoundingBox(ymin=720, xmin=70, ymax=745, xmax=450, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="card_last_four",
                field_label="Card Last 4 Digits",
                section="Transaction Details",
                value="4821",
                confidence=0.97,
                bbox=BoundingBox(ymin=745, xmin=70, ymax=765, xmax=350, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="subtotal",
                field_label="Subtotal",
                section="Totals & Breakdown",
                value="$54.25",
                confidence=0.98,
                bbox=BoundingBox(ymin=490, xmin=650, ymax=515, xmax=850, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="tax_amount",
                field_label="Tax / VAT",
                section="Totals & Breakdown",
                value="$4.68",
                confidence=0.97,
                bbox=BoundingBox(ymin=515, xmin=650, ymax=535, xmax=850, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="tip_amount",
                field_label="Tip / Gratuity",
                section="Totals & Breakdown",
                value="$9.76",
                confidence=0.95,
                bbox=BoundingBox(ymin=538, xmin=650, ymax=558, xmax=850, page=1),
                page_number=1
            ),
            ExtractedFieldItem(
                field_name="total_amount",
                field_label="Grand Total",
                section="Totals & Breakdown",
                value="$68.69",
                confidence=0.99,
                bbox=BoundingBox(ymin=575, xmin=640, ymax=600, xmax=860, page=1),
                page_number=1
            ),
        ]

        table = ExtractedTableItem(
            table_name="Purchased Items",
            columns=["Item Name", "Quantity", "Unit Price", "Total Price"],
            rows=[
                {"item_name": "Single Origin Hayes Valley Espresso", "quantity": "1", "unit_price": "$4.75", "item_total": "$4.75"},
                {"item_name": "New Orleans Iced Coffee (Oat)", "quantity": "2", "unit_price": "$6.50", "item_total": "$13.00"},
                {"item_name": "Almond Croissant (Artisan)", "quantity": "1", "unit_price": "$5.50", "item_total": "$5.50"},
                {"item_name": "Avocado Sourdough Toast", "quantity": "1", "unit_price": "$12.00", "item_total": "$12.00"},
                {"item_name": "Whole Bean Coffee (Bella Donovan 12oz)", "quantity": "1", "unit_price": "$19.00", "item_total": "$19.00"},
            ],
            page_number=1,
            confidence=0.98
        )

        return {"fields": fields, "tables": [table]}

    def extract_generic_or_sample(self, doc_type: str, text: str, filename: str) -> Dict[str, Any]:
        lower_fn = filename.lower()
        if "invoice" in lower_fn or doc_type == "invoice":
            return self.get_sample_invoice_extraction()
        elif "resume" in lower_fn or "cv" in lower_fn or doc_type == "resume":
            return self.get_sample_resume_extraction()
        elif "receipt" in lower_fn or doc_type == "receipt":
            return self.get_sample_receipt_extraction()
        
        # Default to invoice extraction
        return self.get_sample_invoice_extraction()

mock_engine = MockEngine()
