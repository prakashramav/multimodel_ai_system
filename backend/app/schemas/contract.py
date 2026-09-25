from typing import List, Optional, Dict, Any

CONTRACT_SECTIONS = {
    "Agreement Details": [
        ("agreement_title", "Agreement Title", "Title of contract or agreement"),
        ("effective_date", "Effective Date", "Commencement date (YYYY-MM-DD)"),
        ("expiration_date", "Expiration Date", "Termination or expiry date"),
        ("auto_renewal", "Auto-Renewal Clause", "Yes/No or duration if auto-renews"),
        ("governing_law", "Governing Jurisdiction", "State or country governing law")
    ],
    "Parties Involved": [
        ("party_a_name", "Party A (First Party)", "Full legal entity name of First Party"),
        ("party_a_address", "Party A Address", "Registered business address"),
        ("party_b_name", "Party B (Second Party)", "Full legal entity name of Second Party"),
        ("party_b_address", "Party B Address", "Registered business address")
    ],
    "Terms & Financials": [
        ("total_contract_value", "Contract Value", "Financial consideration or total value"),
        ("payment_frequency", "Payment Frequency", "Monthly, annually, milestone-based"),
        ("liability_cap", "Limitation of Liability", "Stated financial liability limit"),
        ("termination_notice_period", "Notice Period", "Days required for termination notice")
    ]
}

CONTRACT_TOOL_SPEC = {
    "name": "extract_contract_data",
    "description": "Extract agreement metadata, parties, legal terms, and clauses from a legal contract.",
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
            "clauses_table": {
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
        "required": ["fields"]
    }
}
