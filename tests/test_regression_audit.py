"""Regression tests for verified security and API defects."""
import math
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from agents.api import app as api_app
from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from esophageal_motility_manometry_agent.server import create_app


def test_hmac_detects_modified_signed_metadata():
    audit = AuditTrail(secret_key="unit-test-secret")
    audit.log("supervisor", "system", "EVALUATION", {"task_id": "SYN-1"})
    assert audit.verify_integrity()
    audit.logs[0]["event_type"] = "FORGED"
    assert not audit.verify_integrity()


def test_hmac_detects_rewritten_signature_and_broken_chain():
    audit = AuditTrail(secret_key="unit-test-secret")
    audit.log("supervisor", "system", "ONE", {"x": "1"})
    audit.log("supervisor", "system", "TWO", {"x": "2"})
    assert audit.verify_integrity()
    audit.logs[0]["current_hash"] = "0" * 64
    assert not audit.verify_integrity()


def test_audit_snapshot_cannot_modify_ledger():
    audit = AuditTrail(secret_key="unit-test-secret")
    audit.log("supervisor", "system", "ONE", {"x": "1"})
    snapshot = audit.get_trail()
    snapshot[0]["current_hash"] = "FORGED"
    assert audit.verify_integrity()
    assert audit.get_trail()[0]["current_hash"] != "FORGED"


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_nonfinite_input_is_rejected(value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T-1", target_identifier="SYN-1", primary_metric=value)


def test_nested_identifier_is_blocked():
    supervisor = SystemSupervisor()
    payload = SystemTaskPayload(
        task_id="T-1", target_identifier="SYN-1", primary_metric=2.0,
        attributes={"unstructured": "SSN 123-45-6789"},
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)


def test_api_returns_client_error_for_blocked_identifier():
    client = TestClient(api_app)
    response = client.post("/api/audit", json={
        "task_id": "T-1", "target_identifier": "SYN-1",
        "primary_metric": 2.0, "attributes": {"note": "MRN-12345678"}
    })
    assert response.status_code == 422
    assert "MRN-12345678" not in response.text


def test_secondary_clinical_api_constructs_and_audits():
    app = create_app()
    assert app is not None
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    response = client.post("/api/audit", json={
        "case_id": "CASE-SYN-1", "patient_synthetic_id": "SYN-1",
        "primary_metric": 12.0, "secondary_metric": 3.0, "status_flag": "NORMAL"
    })
    assert response.status_code == 200, response.text
    assert response.json()["case_id"] == "CASE-SYN-1"
