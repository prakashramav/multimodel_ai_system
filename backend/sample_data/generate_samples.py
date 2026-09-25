import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pypdf

OUTPUT_DIR = Path(__file__).resolve().parent

def create_sample_invoice():
    # 8.5 x 11 inch at 150 DPI = 1275 x 1650
    w, h = 1275, 1650
    img = Image.new("RGB", (w, h), color="#FAFAFA")
    draw = ImageDraw.Draw(img)

    # Top Brand Header bar
    draw.rectangle([(0, 0), (w, 140)], fill="#1E293B")
    draw.text((60, 45), "VERTEX TECHNOLOGIES INC.", fill="#F8FAFC")
    draw.text((60, 85), "Enterprise Cloud Infrastructure & AI Platforms", fill="#94A3B8")

    draw.text((w - 380, 45), "INVOICE", fill="#38BDF8")
    draw.text((w - 380, 85), "ORIGINAL COPY", fill="#CBD5E1")

    # Vendor Block (Left)
    y = 190
    draw.text((60, y), "FROM / VENDOR:", fill="#64748B")
    draw.text((60, y + 25), "Vertex Technologies Inc.", fill="#0F172A")
    draw.text((60, y + 50), "450 Mission Street, Suite 1200", fill="#334155")
    draw.text((60, y + 75), "San Francisco, CA 94105, USA", fill="#334155")
    draw.text((60, y + 100), "Tax ID: US-94-3829104 | VAT: 82910492", fill="#334155")
    draw.text((60, y + 125), "billing@vertexcloud.io | +1 (415) 890-2341", fill="#334155")

    # Meta Block (Right)
    draw.text((w - 450, y), "INVOICE DETAILS:", fill="#64748B")
    draw.text((w - 450, y + 25), "Invoice Number:   INV-2026-8942", fill="#0F172A")
    draw.text((w - 450, y + 50), "Invoice Date:     2026-03-15", fill="#334155")
    draw.text((w - 450, y + 75), "Payment Due Date: 2026-04-14", fill="#334155")
    draw.text((w - 450, y + 100), "PO Number:        PO-9821-X (faint)", fill="#475569")
    draw.text((w - 450, y + 125), "Payment Terms:    Net 30 Days", fill="#334155")

    # Customer / Bill To Block
    y_bill = 370
    draw.rectangle([(50, y_bill), (w - 50, y_bill + 110)], fill="#F1F5F9", outline="#E2E8F0", width=1)
    draw.text((70, y_bill + 15), "BILL TO / CUSTOMER:", fill="#64748B")
    draw.text((70, y_bill + 40), "Horizon Logistics Global Ltd.", fill="#0F172A")
    draw.text((70, y_bill + 65), "742 Evergreen Terrace, Floor 4, Seattle, WA 98101", fill="#334155")
    draw.text((w - 450, y_bill + 40), "Attn: Accounts Payable", fill="#334155")
    draw.text((w - 450, y_bill + 65), "ap@horizonlogistics.com", fill="#2563EB")

    # Line Items Table Header
    y_table = 520
    draw.rectangle([(50, y_table), (w - 50, y_table + 45)], fill="#0F172A")
    draw.text((70, y_table + 12), "ITEM DESCRIPTION", fill="#FFFFFF")
    draw.text((580, y_table + 12), "QTY", fill="#FFFFFF")
    draw.text((700, y_table + 12), "UNIT PRICE", fill="#FFFFFF")
    draw.text((880, y_table + 12), "TAX", fill="#FFFFFF")
    draw.text((1050, y_table + 12), "TOTAL (USD)", fill="#FFFFFF")

    # Line items rows
    items = [
        ("Dedicated GPU Cluster (H100 NVLink) - March 2026", "2", "$4,200.00", "8.5%", "$8,400.00"),
        ("Managed Kubernetes Control Plane Enterprise tier", "1", "$1,250.00", "8.5%", "$1,250.00"),
        ("Distributed S3-Compatible Storage (50 TB Tier)", "50", "$24.00", "8.5%", "$1,200.00"),
        ("Premium 24/7 SLA Technical Support & Dedicated TAM", "1", "$750.00", "0.0%", "$750.00"),
        ("Custom Document Parsing Neural Pipeline Integration", "1", "$3,500.00", "8.5%", "$3,500.00")
    ]

    current_y = y_table + 45
    for i, (desc, qty, unit, tax, tot) in enumerate(items):
        bg = "#FFFFFF" if i % 2 == 0 else "#F8FAFC"
        draw.rectangle([(50, current_y), (w - 50, current_y + 45)], fill=bg, outline="#E2E8F0", width=1)
        draw.text((70, current_y + 12), desc, fill="#1E293B")
        draw.text((590, current_y + 12), qty, fill="#334155")
        draw.text((710, current_y + 12), unit, fill="#334155")
        draw.text((890, current_y + 12), tax, fill="#334155")
        draw.text((1050, current_y + 12), tot, fill="#0F172A")
        current_y += 45

    # Totals block
    y_totals = current_y + 30
    draw.rectangle([(w - 480, y_totals), (w - 50, y_totals + 190)], fill="#FFFFFF", outline="#CBD5E1", width=1)
    
    draw.text((w - 450, y_totals + 15), "Subtotal:", fill="#64748B")
    draw.text((w - 200, y_totals + 15), "$15,100.00", fill="#1E293B")

    draw.text((w - 450, y_totals + 45), "Discount (Partner 5%):", fill="#64748B")
    draw.text((w - 200, y_totals + 45), "- $755.00", fill="#16A34A")

    draw.text((w - 450, y_totals + 75), "Tax (8.5% on eligible):", fill="#64748B")
    draw.text((w - 200, y_totals + 75), "+ $1,219.33", fill="#1E293B")

    draw.text((w - 450, y_totals + 105), "Shipping & Handling:", fill="#64748B")
    draw.text((w - 200, y_totals + 105), "$0.00", fill="#1E293B")

    draw.rectangle([(w - 475, y_totals + 135), (w - 55, y_totals + 180)], fill="#0F172A")
    draw.text((w - 450, y_totals + 148), "TOTAL DUE (USD):", fill="#38BDF8")
    draw.text((w - 200, y_totals + 148), "$15,564.33", fill="#FFFFFF")

    # Bottom Banking Details
    draw.rectangle([(50, y_totals), (w - 520, y_totals + 190)], fill="#F8FAFC", outline="#E2E8F0", width=1)
    draw.text((70, y_totals + 15), "PAYMENT INSTRUCTIONS (WIRE / ACH):", fill="#0F172A")
    draw.text((70, y_totals + 45), "Bank: Silicon Valley Bank, NA", fill="#475569")
    draw.text((70, y_totals + 70), "Account Name: Vertex Technologies Inc.", fill="#475569")
    draw.text((70, y_totals + 95), "Routing Number (ABA): 121000358", fill="#475569")
    draw.text((70, y_totals + 120), "Account Number: 98402918491", fill="#475569")
    draw.text((70, y_totals + 145), "Note: Please include INV-2026-8942 in payment reference", fill="#64748B")

    # Footer note
    draw.text((60, h - 80), "Vertex Technologies Inc. | Support: support@vertexcloud.io | Thank you for your business!", fill="#94A3B8")

    pdf_path = OUTPUT_DIR / "sample_invoice.pdf"
    png_path = OUTPUT_DIR / "sample_invoice.png"
    img.save(png_path, "PNG")
    img.save(pdf_path, "PDF", resolution=150.0)
    print("Created sample invoice:", pdf_path)

def create_sample_resume():
    w, h = 1275, 1650
    img = Image.new("RGB", (w, h), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    # Header Name & Title
    draw.rectangle([(0, 0), (w, 160)], fill="#0F172A")
    draw.text((60, 35), "ALEX MORGAN", fill="#F8FAFC")
    draw.text((60, 75), "Staff AI Systems Engineer & Full-Stack Architect", fill="#38BDF8")
    draw.text((60, 110), "alex.morgan.ai@example.com  |  +1 (650) 492-8172  |  San Francisco, CA  |  github.com/alexmorgan-ai", fill="#94A3B8")

    # Summary
    y = 190
    draw.text((60, y), "PROFESSIONAL SUMMARY", fill="#0F172A")
    draw.line([(60, y + 22), (w - 60, y + 22)], fill="#CBD5E1", width=2)
    summary_text = (
        "Staff Software Engineer with 8+ years architecting enterprise multimodal AI platforms, high-throughput distributed systems,\n"
        "and production LLM extraction pipelines. Proven track record scaling document intelligence workflows processing 10M+ docs/month."
    )
    draw.text((60, y + 35), summary_text, fill="#334155")

    # Skills Section
    y = 290
    draw.text((60, y), "CORE TECHNICAL SKILLS", fill="#0F172A")
    draw.line([(60, y + 22), (w - 60, y + 22)], fill="#CBD5E1", width=2)
    draw.text((60, y + 35), "Languages & Frameworks: Python, TypeScript, FastAPI, Next.js, PyTorch, SQLAlchemy, React, Go", fill="#1E293B")
    draw.text((60, y + 60), "AI & Multimodal: Claude Vision APIs, OpenAI, Transformers, LangChain, DocVQA, RAG, Tesseract OCR", fill="#1E293B")
    draw.text((60, y + 85), "Cloud & Infra: AWS (S3, ECS, Lambda), Docker, PostgreSQL, Redis, Kubernetes, Kafka, CI/CD", fill="#1E293B")

    # Experience Section
    y = 420
    draw.text((60, y), "PROFESSIONAL EXPERIENCE", fill="#0F172A")
    draw.line([(60, y + 22), (w - 60, y + 22)], fill="#CBD5E1", width=2)

    # Job 1
    y += 35
    draw.text((60, y), "Staff AI Platform Engineer — ScaleAI Technologies", fill="#0F172A")
    draw.text((w - 280, y), "2023 - Present", fill="#64748B")
    draw.text((60, y + 25), "San Francisco, CA", fill="#64748B")
    j1_bullets = [
        "• Spearheaded multimodal document intelligence architecture using vision models and dynamic JSON schema enforcement.",
        "• Reduced extraction latency by 45% using async pipeline queuing with Celery/Redis and PyMuPDF hardware acceleration.",
        "• Implemented human-in-the-loop verification portal cutting false positive validation rates from 8.2% to under 0.4%."
    ]
    for b in j1_bullets:
        y += 25
        draw.text((80, y), b, fill="#334155")

    # Job 2
    y += 45
    draw.text((60, y), "Senior Backend Engineer — NeuralDocs Inc.", fill="#0F172A")
    draw.text((w - 280, y), "2020 - 2023", fill="#64748B")
    draw.text((60, y + 25), "Seattle, WA (Remote)", fill="#64748B")
    j2_bullets = [
        "• Built high-concurrency OCR ingestion microservices handling 250+ requests/sec using FastAPI and PostgreSQL.",
        "• Engineered automated table detection & extraction parser converting complex scanned financial reports to structured JSON.",
        "• Deployed semantic Q&A search over multi-page contracts using hybrid vector embeddings and keyword BM25."
    ]
    for b in j2_bullets:
        y += 25
        draw.text((80, y), b, fill="#334155")

    # Job 3
    y += 45
    draw.text((60, y), "Software Engineer — CloudMatrix Solutions", fill="#0F172A")
    draw.text((w - 280, y), "2018 - 2020", fill="#64748B")
    draw.text((60, y + 25), "Austin, TX", fill="#64748B")
    j3_bullets = [
        "• Designed and maintained REST APIs and real-time dashboard analytics with React and Python.",
        "• Automated infrastructure provisioning using Terraform and AWS CloudFormation."
    ]
    for b in j3_bullets:
        y += 25
        draw.text((80, y), b, fill="#334155")

    # Education Section
    y += 55
    draw.text((60, y), "EDUCATION & CERTIFICATIONS", fill="#0F172A")
    draw.line([(60, y + 22), (w - 60, y + 22)], fill="#CBD5E1", width=2)
    y += 35
    draw.text((60, y), "Master of Science in Computer Science (Specialization: Machine Learning)", fill="#0F172A")
    draw.text((w - 280, y), "2016 - 2018", fill="#64748B")
    draw.text((60, y + 25), "University of Washington, Seattle | GPA: 3.92 / 4.0", fill="#334155")

    y += 55
    draw.text((60, y), "Bachelor of Science in Software Engineering", fill="#0F172A")
    draw.text((w - 280, y), "2012 - 2016", fill="#64748B")
    draw.text((60, y + 25), "University of Texas at Austin | Magna Cum Laude", fill="#334155")

    pdf_path = OUTPUT_DIR / "sample_resume.pdf"
    png_path = OUTPUT_DIR / "sample_resume.png"
    img.save(png_path, "PNG")
    img.save(pdf_path, "PDF", resolution=150.0)
    print("Created sample resume:", pdf_path)

def create_sample_receipt():
    # Receipt layout: standard narrow receipt format, e.g. 700 x 1400
    w, h = 800, 1400
    img = Image.new("RGB", (w, h), color="#FFFDF7")
    draw = ImageDraw.Draw(img)

    # Merchant header
    y = 50
    draw.text((w // 2 - 170, y), "*** BLUE BOTTLE COFFEE ***", fill="#0F172A")
    draw.text((w // 2 - 130, y + 30), "Mint Plaza Espresso Bar", fill="#334155")
    draw.text((w // 2 - 150, y + 55), "315 Linden St, San Francisco, CA", fill="#475569")
    draw.text((w // 2 - 90, y + 80), "Tel: (415) 252-7735", fill="#64748B")
    draw.text((w // 2 - 110, y + 105), "Tax Reg: CA-94829103-01", fill="#64748B")

    draw.line([(40, y + 140), (w - 40, y + 140)], fill="#CBD5E1", width=1)

    # Metadata
    y = 210
    draw.text((50, y), "Receipt #:    RCP-839201", fill="#1E293B")
    draw.text((w - 280, y), "Station: 02", fill="#1E293B")
    draw.text((50, y + 25), "Date:         2026-03-24", fill="#1E293B")
    draw.text((w - 280, y + 25), "Time:    10:14 AM", fill="#1E293B")
    draw.text((50, y + 50), "Server:       Marcus K.", fill="#1E293B")
    draw.text((w - 280, y + 50), "Order:   Takeout", fill="#1E293B")

    draw.line([(40, y + 85), (w - 40, y + 85)], fill="#0F172A", width=2)

    # Items Header
    y = 310
    draw.text((50, y), "ITEM", fill="#0F172A")
    draw.text((450, y), "QTY", fill="#0F172A")
    draw.text((560, y), "PRICE", fill="#0F172A")
    draw.text((680, y), "TOTAL", fill="#0F172A")
    draw.line([(40, y + 25), (w - 40, y + 25)], fill="#CBD5E1", width=1)

    items = [
        ("Single Origin Hayes Valley Espresso", "1", "$4.75", "$4.75"),
        ("New Orleans Iced Coffee (Oat)", "2", "$6.50", "$13.00"),
        ("Almond Croissant (Artisan)", "1", "$5.50", "$5.50"),
        ("Avocado Sourdough Toast", "1", "$12.00", "$12.00"),
        ("Whole Bean Coffee (Bella Donovan 12oz)", "1", "$19.00", "$19.00")
    ]

    current_y = y + 40
    for name, qty, price, total in items:
        draw.text((50, current_y), name, fill="#334155")
        draw.text((460, current_y), qty, fill="#334155")
        draw.text((560, current_y), price, fill="#334155")
        draw.text((680, current_y), total, fill="#0F172A")
        current_y += 35

    draw.line([(40, current_y + 15), (w - 40, current_y + 15)], fill="#CBD5E1", width=1)

    # Totals
    y_tot = current_y + 35
    draw.text((450, y_tot), "Subtotal:", fill="#475569")
    draw.text((680, y_tot), "$54.25", fill="#0F172A")

    draw.text((450, y_tot + 30), "Sales Tax (8.625%):", fill="#475569")
    draw.text((680, y_tot + 30), "$4.68", fill="#0F172A")

    draw.text((450, y_tot + 60), "Tip (18%):", fill="#475569")
    draw.text((680, y_tot + 60), "$9.76", fill="#0F172A")

    draw.line([(440, y_tot + 95), (w - 50, y_tot + 95)], fill="#0F172A", width=2)
    draw.text((450, y_tot + 110), "TOTAL PAID:", fill="#0F172A")
    draw.text((660, y_tot + 110), "$68.69", fill="#0F172A")

    # Payment details
    y_pay = y_tot + 170
    draw.rectangle([(50, y_pay), (w - 50, y_pay + 100)], fill="#F1F5F9", outline="#E2E8F0")
    draw.text((70, y_pay + 15), "PAYMENT METHOD: Visa Contactless", fill="#1E293B")
    draw.text((70, y_pay + 40), "Card: ************4821  |  Auth: 09281A", fill="#475569")
    draw.text((70, y_pay + 65), "AID: A0000000031010  |  Status: APPROVED", fill="#16A34A")

    # Barcode/Footer
    draw.line([(40, y_pay + 130), (w - 40, y_pay + 130)], fill="#CBD5E1", width=1)
    draw.text((w // 2 - 120, y_pay + 150), "THANK YOU FOR VISITING!", fill="#64748B")
    draw.text((w // 2 - 140, y_pay + 175), "Visit us online at bluebottlecoffee.com", fill="#94A3B8")

    pdf_path = OUTPUT_DIR / "sample_receipt.pdf"
    png_path = OUTPUT_DIR / "sample_receipt.png"
    img.save(png_path, "PNG")
    img.save(pdf_path, "PDF", resolution=150.0)
    print("Created sample receipt:", pdf_path)

if __name__ == "__main__":
    create_sample_invoice()
    create_sample_resume()
    create_sample_receipt()
