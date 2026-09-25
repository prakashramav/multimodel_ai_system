from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    ymin: float = Field(..., description="Top coordinate (0-1000 or 0-100% normalized)")
    xmin: float = Field(..., description="Left coordinate (0-1000 or 0-100% normalized)")
    ymax: float = Field(..., description="Bottom coordinate (0-1000 or 0-100% normalized)")
    xmax: float = Field(..., description="Right coordinate (0-1000 or 0-100% normalized)")
    page: int = Field(default=1, description="1-indexed page number")

class ExtractedFieldItem(BaseModel):
    field_name: str
    field_label: str
    value: Union[str, int, float, bool, None]
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    bbox: Optional[BoundingBox] = None
    section: str = "General"
    page_number: int = 1

class ExtractedTableItem(BaseModel):
    table_name: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    page_number: int = 1
    confidence: float = 1.0

class ClassificationOutput(BaseModel):
    document_type: str = Field(
        ...,
        description="One of: invoice, resume, receipt, contract, form, other"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Brief visual and textual reasoning")

class ExtractionResult(BaseModel):
    classification: ClassificationOutput
    fields: List[ExtractedFieldItem]
    tables: List[ExtractedTableItem]
