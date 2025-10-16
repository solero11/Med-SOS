from src.utils.clinician_query import ClinicianQueryAssistant
from src.utils.sbar_builder import SBAR


def test_clinician_query_assistant_prioritizes_vital_updates():
    assistant = ClinicianQueryAssistant()
    sbar = SBAR(situation="sat dropping 85", background=None, assessment=None, recommendation=None)
    questions = assistant.generate(
        sbar=sbar,
        event_text="sat now eighty five heart rate one-ten",
        protocols=[],
    )
    assert questions
    assert any("oxygen" in q.lower() for q in questions)


def test_clinician_query_assistant_handles_missing_fields():
    assistant = ClinicianQueryAssistant()
    sbar = SBAR(situation="BP 70/40", background=None, assessment=None, recommendation=None)
    questions = assistant.generate(
        sbar=sbar,
        event_text="clinician reports no additional information yet",
        protocols=[],
    )
    assert questions
    assert any("background" in q.lower() or "comorbidities" in q.lower() for q in questions)
