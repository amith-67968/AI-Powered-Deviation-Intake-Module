from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Impact = Literal["Low", "Medium", "High", "Critical"]
Severity = Literal["Minor", "Moderate", "Major", "Critical"]
Source = Literal["Production", "Quality Control", "Quality Assurance", "Maintenance", "Laboratory", "Other"]
Status = Literal["Draft", "Submitted", "Under Review", "Closed"]


class ExtractionOutput(BaseModel):
    site: str | None = None
    date_of_occurrence: date | None = None
    title: str | None = None
    source: Source | None = None
    product_material: str | None = None
    batch_lot_number: str | None = None
    detailed_description: str | None = None
    initial_impact: Impact | None = None
    initial_severity: Severity | None = None
    confidence: float = Field(default=0, ge=0, le=1)
    missing_information: list[str] = Field(default_factory=list)


class RecommendationOutput(BaseModel):
    impact: Impact | None = None
    severity: Severity | None = None
    reason: str = "Human QA review is required before classification."


class AnalysisResponse(BaseModel):
    extraction: ExtractionOutput
    recommendation: RecommendationOutput
    processing_steps: list[str] = Field(default_factory=list)


class DeviationBase(BaseModel):
    site: str | None = None
    date_of_occurrence: date | None = None
    title: str = Field(min_length=3, max_length=500)
    source: Source | None = None
    product_material: str | None = None
    batch_lot_number: str | None = None
    detailed_description: str = Field(min_length=10)
    initial_impact: Impact | None = None
    initial_severity: Severity | None = None
    ai_recommended_impact: Impact | None = None
    ai_recommended_severity: Severity | None = None
    ai_severity_reason: str | None = None
    ai_confidence: float | None = Field(default=None, ge=0, le=1)
    ai_extracted_data: dict | None = None
    status: Status = "Draft"


class DeviationCreate(DeviationBase):
    pass


class DeviationUpdate(DeviationBase):
    pass


class DeviationRead(DeviationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1500)
    deviation_context: dict = Field(default_factory=dict)


class ChatResponse(BaseModel):
    answer: str
