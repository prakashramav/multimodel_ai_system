from typing import List, Optional, Dict, Any

RECEIPT_SECTIONS = {
    "Merchant Details": [
        ("merchant_name", "Merchant / Store Name", "Name of business issuing receipt"),
        ("merchant_address", "Store Address", "Physical store location"),
        ("merchant_phone", "Store Phone", "Telephone number"),
        ("tax_id", "Tax / VAT ID", "Merchant tax registration number")
    ],
    "Transaction Details": [
        ("receipt_number", "Receipt / Check #", "Transaction or ticket sequence number"),
        ("transaction_date", "Date", "Date of sale (YYYY-MM-DD)"),
        ("transaction_time", "Time", "Time of sale (HH:MM:SS)"),
        ("cashier_id", "Server / Cashier", "Terminal or cashier identifier"),
        ("payment_method", "Payment Method", "Cash, Credit Card, Apple Pay, etc."),
        ("card_last_four", "Card Last 4 Digits", "Last 4 digits of payment card")
    ],
    "Totals & Breakdown": [
        ("currency", "Currency", "Currency code or symbol"),
        ("subtotal", "Subtotal", "Subtotal before taxes"),
        ("discount", "Discount", "Discount deducted"),
        ("tax_amount", "Tax / VAT", "Sales tax or VAT charged"),
        ("tip_amount", "Tip / Gratuity", "Added gratuity or tip"),
        ("total_amount", "Grand Total", "Total amount charged/paid")
    ]
}

RECEIPT_TOOL_SPEC = {
    "name": "extract_receipt_data",
    "description": "Extract merchant info, transaction metadata, itemized items table, and totals from a receipt.",
    "input_schema": {
        "type": "object",
        "properties": {
            "fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "field_name": {"type": "string"},
                        "field_label": {"type": "string"},
                        "section": {"type": "string"},
                        "value": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "page_number": {"type": "integer", "default": 1},
                        "bounding_box": {
                            "type": "object",
                            "properties": {
                                "ymin": {"type": "number"},
                                "xmin": {"type": "number"},
                                "ymax": {"type": "number"},
                                "xmax": {"type": "number"},
                                "page": {"type": "integer", "default": 1}
                            },
                            "required": ["ymin", "xmin", "ymax", "xmax"]
                        }
                    },
                    "required": ["field_name", "field_label", "section", "value", "confidence"]
                }
            },
            "purchased_items_table": {
                "type": "object",
                "properties": {
                    "columns": {"type": "array", "items": {"type": "string"}},
                    "rows": {
                        "type": "array",
                        "items": {"type": "object", "additionalProperties": {"type": "string"}}
                    }
                },
                "required": ["columns", "rows"]
            }
        },
        "required": ["fields", "purchased_items_table"]
    }
}
