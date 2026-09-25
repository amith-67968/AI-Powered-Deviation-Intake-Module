from datetime import date, datetime
from typing import Any
from sqlalchemy import Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON
from app.db.session import Base

JsonType = JSON().with_variant(JSONB, "postgresql")


class Deviation(Base):
    __tablename__ = "deviations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site: Mapped[str | None] = mapped_column(String(255))
    date_of_occurrence: Mapped[date | None] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str | None] = mapped_column(String(100))
    product_material: Mapped[str | None] = mapped_column(String(255))
    batch_lot_number: Mapped[str | None] = mapped_column(String(255))
    detailed_description: Mapped[str] = mapped_column(Text, nullable=False)
    initial_impact: Mapped[str | None] = mapped_column(String(50))
    initial_severity: Mapped[str | None] = mapped_column(String(50))
    ai_recommended_impact: Mapped[str | None] = mapped_column(String(50))
    ai_recommended_severity: Mapped[str | None] = mapped_column(String(50))
    ai_severity_reason: Mapped[str | None] = mapped_column(Text)
    ai_confidence: Mapped[float | None] = mapped_column(Float)
    ai_extracted_data: Mapped[dict[str, Any] | None] = mapped_column(JsonType)
    status: Mapped[str] = mapped_column(String(50), default="Draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
