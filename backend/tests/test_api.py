import os
os.environ["DATABASE_URL"] = "sqlite:///./test_deviations.db"

from fastapi.testclient import TestClient
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable
from app.db.session import Base, engine
from app.main import app
from app.models.deviation import Deviation
from app.schemas.deviation import AnalysisResponse, ExtractionOutput, RecommendationOutput

Base.metadata.create_all(engine)
client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["database"] == "connected"


def test_deviation_schema_compiles_for_postgresql():
    ddl = str(CreateTable(Deviation.__table__).compile(dialect=postgresql.dialect()))
    assert "JSONB" in ddl
    assert "TIMESTAMP WITH TIME ZONE" in ddl


def test_analyze_requires_input():
    response = client.post("/api/deviations/analyze")
    assert response.status_code == 422


def test_analyze_rejects_invalid_file_type():
    response = client.post(
        "/api/deviations/analyze",
        files={"file": ("notes.xlsx", b"not supported", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 415


def test_analyze_returns_validated_structured_response(monkeypatch):
    async def fake_graph(text):
        assert "temperature" in text.lower()
        return AnalysisResponse(
            extraction=ExtractionOutput(site="API Manufacturing Unit", title="Temperature excursion", detailed_description="Temperature was observed above the approved range.", confidence=.88, missing_information=["Duration confirmation"]),
            recommendation=RecommendationOutput(impact="High", severity="Major", reason="AI recommendation requiring human QA review."),
            processing_steps=["Analysis complete"],
        )
    monkeypatch.setattr("app.api.routes.deviations.run_deviation_graph", fake_graph)
    response = client.post("/api/deviations/analyze", data={"text": "The temperature was high."})
    assert response.status_code == 200
    assert response.json()["recommendation"]["severity"] == "Major"


def test_deviation_crud_lifecycle():
    payload = {"site": "API Manufacturing Unit", "date_of_occurrence": "2026-09-24", "title": "Temperature excursion", "source": "Production", "product_material": "API Intermediate X", "batch_lot_number": "API-260924-B17", "detailed_description": "Temperature exceeded approved range during routine manufacturing monitoring.", "initial_impact": "High", "initial_severity": "Major", "status": "Draft"}
    saved = client.post("/api/deviations", json=payload)
    assert saved.status_code == 201
    deviation_id = saved.json()["id"]

    records = client.get("/api/deviations")
    assert records.status_code == 200
    assert any(record["id"] == deviation_id for record in records.json())

    record = client.get(f"/api/deviations/{deviation_id}")
    assert record.status_code == 200
    assert record.json()["title"] == payload["title"]

    payload["title"] = "Temperature excursion - reviewed"
    updated = client.put(f"/api/deviations/{deviation_id}", json=payload)
    assert updated.status_code == 200
    assert updated.json()["title"] == payload["title"]

    deleted = client.delete(f"/api/deviations/{deviation_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/deviations/{deviation_id}").status_code == 404
