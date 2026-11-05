import pytest
from pydantic import ValidationError
from src.schemas import NonConformityReport, SeverityLevel
from src.agent import InspectionAgent

def test_valid_schema_instantiation():
    valid_data = {
        "item_id": "ASY-9901",
        "defect_category": "Delaminação de Composto",
        "severity": SeverityLevel.HIGH.value,
        "detected_evidence": ["Dano visível no bordo de ataque"],
        "missing_fields": [],
        "bilingual_summary": {
            "pt_BR": "Delaminação constatada no bordo de ataque.",
            "en_US": "Delamination detected on leading edge."
        },
        "is_valid_for_submission": True
    }
    report = NonConformityReport(**valid_data)
    assert report.item_id == "ASY-9901"
    assert report.is_valid_for_submission is True

def test_schema_bilingual_validation_failure():
    invalid_data = {
        "item_id": "ASY-9901",
        "defect_category": "Desvio",
        "severity": SeverityLevel.LOW.value,
        "bilingual_summary": {"pt_BR": "Apenas português"},
        "is_valid_for_submission": False
    }
    with pytest.raises(ValidationError):
        NonConformityReport(**invalid_data)

def test_agent_workflow_missing_fields():
    agent = InspectionAgent()
    result = agent.run("Apenas um parafuso frouxo")
    assert result.status == "ACTION_REQUIRED"
    assert result.report.is_valid_for_submission is False
    assert len(result.report.missing_fields) > 0
