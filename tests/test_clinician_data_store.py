from pathlib import Path

from src.utils.clinician_data_store import ClinicianDataStore

SCENE_DIR = Path(__file__).resolve().parents[1] / "scenes" / "tension_pneumo"


def test_data_store_returns_latest_vital():
    store = ClinicianDataStore.from_path(SCENE_DIR / "clinician_data.yaml")
    question = "Could you update the current blood pressure?"
    response = store.respond(question, event_time=200.0)
    assert "95/50" in response or "70/40" in response


def test_data_store_handles_medication_queries():
    store = ClinicianDataStore.from_path(SCENE_DIR / "clinician_data.yaml")
    response = store.respond("Which medications were given most recently?", event_time=150.0)
    assert "phenylephrine" in response.lower() or "albuterol" in response.lower()


def test_data_store_handles_lab_and_imaging():
    store = ClinicianDataStore.from_path(SCENE_DIR / "clinician_data.yaml")
    lab_response = store.respond("Any recent blood gas values?", event_time=220.0)
    lower_lab = lab_response.lower()
    assert "abg" in lower_lab or "hemoglobin" in lower_lab
    imaging_response = store.respond("What did ultrasound show?", event_time=220.0)
    assert "pocus" in imaging_response.lower()
