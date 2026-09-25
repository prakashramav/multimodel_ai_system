from typing import Dict, Any, List
from backend.app.schemas.invoice import INVOICE_SECTIONS, INVOICE_TOOL_SPEC
from backend.app.schemas.resume import RESUME_SECTIONS, RESUME_TOOL_SPEC
from backend.app.schemas.receipt import RECEIPT_SECTIONS, RECEIPT_TOOL_SPEC
from backend.app.schemas.contract import CONTRACT_SECTIONS, CONTRACT_TOOL_SPEC

SUPPORTED_DOCUMENT_TYPES = [
    "invoice",
    "resume",
    "receipt",
    "contract",
    "form",
    "other"
]

SCHEMA_REGISTRY: Dict[str, Dict[str, Any]] = {
    "invoice": {
        "label": "Commercial Invoice",
        "sections": INVOICE_SECTIONS,
        "tool_spec": INVOICE_TOOL_SPEC,
        "default_table_name": "Line Items",
    },
    "resume": {
        "label": "Professional Resume / CV",
        "sections": RESUME_SECTIONS,
        "tool_spec": RESUME_TOOL_SPEC,
        "default_table_name": "Work Experience",
    },
    "receipt": {
        "label": "Store / Expense Receipt",
        "sections": RECEIPT_SECTIONS,
        "tool_spec": RECEIPT_TOOL_SPEC,
        "default_table_name": "Purchased Items",
    },
    "contract": {
        "label": "Legal Agreement / Contract",
        "sections": CONTRACT_SECTIONS,
        "tool_spec": CONTRACT_TOOL_SPEC,
        "default_table_name": "Key Clauses",
    }
}

def get_schema_for_type(doc_type: str) -> Dict[str, Any]:
    norm_type = (doc_type or "").lower().strip()
    if norm_type in SCHEMA_REGISTRY:
        return SCHEMA_REGISTRY[norm_type]
    # Default fallback to invoice structure for structured documents
    return SCHEMA_REGISTRY["invoice"]
