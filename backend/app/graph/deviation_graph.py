import json
import logging
from typing import Any, TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from app.ai.prompts import IMPACT_PROMPT, SEVERITY_PROMPT, EXTRACTION_PROMPT, VALIDATION_PROMPT
from app.core.config import get_settings
from app.schemas.deviation import AnalysisResponse, ExtractionOutput, RecommendationOutput

logger = logging.getLogger(__name__)


class DeviationState(TypedDict, total=False):
    raw_input: str
    extracted_text: str
    extracted_deviation: dict[str, Any]
    validation_errors: list[str]
    impact: str | None
    severity: str | None
    severity_reason: str
    confidence: float
    missing_information: list[str]
    processing_steps: list[str]
    final_result: AnalysisResponse


def _model(schema):
    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError("Groq is not configured")
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0,
    ).with_structured_output(schema, method="json_schema", strict=True)


def ingest_input(state: DeviationState) -> DeviationState:
    return {"extracted_text": state["raw_input"].strip(), "processing_steps": ["Input received"]}


def extract_text(state: DeviationState) -> DeviationState:
    # File parsing occurs before the graph. This node normalizes text supplied to the AI workflow.
    return {"extracted_text": state["extracted_text"], "processing_steps": state["processing_steps"] + ["Document text prepared"]}


def extract_deviation(state: DeviationState) -> DeviationState:
    result = _model(ExtractionOutput).invoke(EXTRACTION_PROMPT.format(source=state["extracted_text"]))
    return {"extracted_deviation": result.model_dump(mode="json"), "processing_steps": state["processing_steps"] + ["Structured deviation information extracted"]}


def validate_extraction(state: DeviationState) -> DeviationState:
    proposed = json.dumps(state["extracted_deviation"], default=str)
    result = _model(ExtractionOutput).invoke(VALIDATION_PROMPT.format(source=state["extracted_text"], extraction=proposed))
    return {
        "extracted_deviation": result.model_dump(mode="json"),
        "confidence": result.confidence,
        "missing_information": result.missing_information,
        "validation_errors": [],
        "processing_steps": state["processing_steps"] + ["Extraction validated against source"],
    }


def impact_analysis(state: DeviationState) -> DeviationState:
    result = _model(RecommendationOutput).invoke(IMPACT_PROMPT.format(deviation=json.dumps(state["extracted_deviation"], default=str)))
    return {"impact": result.impact, "processing_steps": state["processing_steps"] + ["Potential impact assessed"]}


def severity_analysis(state: DeviationState) -> DeviationState:
    result = _model(RecommendationOutput).invoke(SEVERITY_PROMPT.format(deviation=json.dumps(state["extracted_deviation"], default=str), impact=state.get("impact")))
    return {"severity": result.severity, "severity_reason": result.reason, "processing_steps": state["processing_steps"] + ["Suggested severity determined"]}


def generate_explanation(state: DeviationState) -> DeviationState:
    return {"processing_steps": state["processing_steps"] + ["Recommendation reasoning prepared"]}


def finalize_result(state: DeviationState) -> DeviationState:
    extraction = ExtractionOutput.model_validate(state["extracted_deviation"])
    recommendation = RecommendationOutput(impact=state.get("impact"), severity=state.get("severity"), reason=state.get("severity_reason") or "Human QA review is required before classification.")
    result = AnalysisResponse(extraction=extraction, recommendation=recommendation, processing_steps=state["processing_steps"] + ["Analysis complete"])
    return {"final_result": result}


def build_graph():
    graph = StateGraph(DeviationState)
    graph.add_node("ingest_input", ingest_input)
    graph.add_node("extract_text", extract_text)
    graph.add_node("extract_deviation", extract_deviation)
    graph.add_node("validate_extraction", validate_extraction)
    graph.add_node("impact_analysis", impact_analysis)
    graph.add_node("severity_analysis", severity_analysis)
    graph.add_node("generate_explanation", generate_explanation)
    graph.add_node("finalize_result", finalize_result)
    graph.add_edge(START, "ingest_input")
    graph.add_edge("ingest_input", "extract_text")
    graph.add_edge("extract_text", "extract_deviation")
    graph.add_edge("extract_deviation", "validate_extraction")
    graph.add_edge("validate_extraction", "impact_analysis")
    graph.add_edge("impact_analysis", "severity_analysis")
    graph.add_edge("severity_analysis", "generate_explanation")
    graph.add_edge("generate_explanation", "finalize_result")
    graph.add_edge("finalize_result", END)
    return graph.compile()


async def run_deviation_graph(text: str) -> AnalysisResponse:
    if not text.strip():
        raise ValueError("Deviation text is required")
    try:
        state = await build_graph().ainvoke({"raw_input": text})
        return state["final_result"]
    except RuntimeError:
        raise
    except Exception:
        logger.exception("Deviation LangGraph workflow failed")
        raise RuntimeError("Unable to analyze the deviation. Please try again.")
