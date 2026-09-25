from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

INVOICE_SECTIONS = {
    "Vendor Details": [
        ("vendor_name", "Vendor Name", "Name of company or individual issuing the invoice"),
        ("vendor_address", "Vendor Address", "Full street/mailing address of the vendor"),
        ("vendor_tax_id", "Vendor Tax ID / VAT", "Tax ID, VAT number, or EIN"),
        ("vendor_phone", "Vendor Phone", "Contact telephone number"),
        ("vendor_email", "Vendor Email", "Contact email address")
    ],
    "Invoice Details": [
        ("invoice_number", "Invoice Number", "Unique invoice reference number"),
        ("invoice_date", "Invoice Date", "Date invoice was issued (YYYY-MM-DD)"),
        ("due_date", "Payment Due Date", "Payment due date (YYYY-MM-DD)"),
        ("purchase_order_number", "PO Number", "Associated purchase order reference"),
        ("payment_terms", "Payment Terms", "Terms such as Net 30, Due on Receipt")
    ],
    "Customer Details": [
        ("customer_name", "Customer / Bill To", "Name of billed client or organization"),
        ("customer_address", "Billing Address", "Billing address of customer"),
        ("customer_email", "Customer Email", "Email address of customer"),
        ("customer_phone", "Customer Phone", "Phone number of customer")
    ],
    "Totals & Financials": [
        ("currency", "Currency", "Currency symbol or code (e.g. USD, EUR, INR)"),
        ("subtotal", "Subtotal", "Subtotal before tax and discounts"),
        ("tax_rate", "Tax Rate (%)", "Tax or VAT percentage rate"),
        ("tax_amount", "Tax Amount", "Total tax calculated"),
        ("discount_amount", "Discount", "Discounts applied"),
        ("shipping_fee", "Shipping Fee", "Shipping or freight charge"),
        ("total_amount", "Total Amount Due", "Grand total payable")
    ]
}

INVOICE_TOOL_SPEC = {
    "name": "extract_invoice_data",
    "description": "Extract structured fields, confidence scores, bounding boxes, and line items table from an invoice document.",
    "input_schema": {
        "type": "object",
        "properties": {
            "fields": {
                "type": "array",
                "description": "List of key-value fields found in the invoice",
                "items": {
                    "type": "object",
                    "properties": {
                        "field_name": {"type": "string"},
                        "field_label": {"type": "string"},
                        "section": {"type": "string"},
                        "value": {"type": "string", "description": "Extracted text or numeric value"},
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "page_number": {"type": "integer", "default": 1},
                        "bounding_box": {
                            "type": "object",
                            "properties": {
                                "ymin": {"type": "number", "description": "0-1000 top edge"},
                                "xmin": {"type": "number", "description": "0-1000 left edge"},
                                "ymax": {"type": "number", "description": "0-1000 bottom edge"},
                                "xmax": {"type": "number", "description": "0-1000 right edge"},
                                "page": {"type": "integer", "default": 1}
                            },
                            "required": ["ymin", "xmin", "ymax", "xmax"]
                        }
                    },
                    "required": ["field_name", "field_label", "section", "value", "confidence"]
                }
            },
            "line_items_table": {
                "type": "object",
                "description": "Table of line items/products billed",
                "properties": {
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "rows": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": {"type": "string"}
                        }
                    }
                },
                "required": ["columns", "rows"]
            }
        },
        "required": ["fields", "line_items_table"]
    }
}
