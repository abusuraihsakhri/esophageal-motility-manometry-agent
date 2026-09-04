"""
Security and Reliability Tests for Esophageal Motility Manometry Agent.
Tests for PHI guard, audit trail, batch error handling, and input validation.
"""
import sys
import os
import csv
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import (
    PHIGuard,
    AuditTrail,
    AuditLogger,
    SecurityException,
    assert_no_phi,
)
from agents.models import SystemTaskPayload, UrgencyLevel
from agents.supervisor import SystemSupervisor


class TestPHIGuard:
    """Tests for PHI outbound guard security."""

    def test_ssn_pattern_blocked(self):
        with pytest.raises(SecurityException) as exc_info:
            PHIGuard.assert_no_phi("Patient SSN: 123-45-6789")
        assert "pattern" not in str(exc_info.value)
        assert "PHI Outbound Guard Violation" in str(exc_info.value)

    def test_mrn_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("MRN-12345678 clinical note")

    def test_phone_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Contact patient at 555-123-4567")

    def test_email_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Send results to patient@example.com")

    def test_dob_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("DOB: 01/15/1985")

    def test_patient_name_pattern_blocked(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient Name: John Smith")

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")
        PHIGuard.assert_no_phi("Metric value 24.5 within normal range")

    def test_empty_text_passes(self):
        PHIGuard.assert_no_phi("")

    def test_none_text_passes(self):
        PHIGuard.assert_no_phi(None)

    def test_redact_phi(self):
        result = PHIGuard.redact_phi("Patient MRN-12345678 has SSN 123-45-6789")
        assert "MRN" not in result
        assert "123-45-6789" not in result
        assert "[REDACTED_IDENTIFIER]" in result


class TestAuditTrail:
    """Tests for HMAC-SHA256 audit trail integrity."""

    def test_audit_trail_chaining(self):
        trail = AuditTrail(secret_key="test-key-2026")
        trail.log("actor1", "tier1", "EVENT_A", {"data": "value1"})
        trail.log("actor2", "tier2", "EVENT_B", {"data": "value2"})
        assert trail.verify_integrity() is True
        assert len(trail.get_trail()) == 2

    def test_audit_trail_tamper_detection(self):
        trail = AuditTrail(secret_key="test-key-2026")
        trail.log("actor1", "tier1", "EVENT_A", {"data": "value1"})
        trail.log("actor2", "tier2", "EVENT_B", {"data": "value2"})
        # Tamper with the first entry
        trail.logs[0]["current_hash"] = "TAMPERED_HASH"
        assert trail.verify_integrity() is False

    def test_audit_trail_phi_blocked(self):
        trail = AuditTrail(secret_key="test-key-2026")
        with pytest.raises(SecurityException):
            trail.log("actor1", "tier1", "EVENT_A", {"patient_ssn": "123-45-6789"})

    def test_audit_trail_with_env_key(self):
        os.environ["AUDIT_SECRET_KEY"] = "env-based-key-2026"
        trail = AuditTrail()
        trail.log("actor1", "tier1", "EVENT_A", {"data": "value1"})
        assert trail.verify_integrity() is True
        del os.environ["AUDIT_SECRET_KEY"]


class TestBatchProcessing:
    """Tests for batch CSV processing error handling."""

    def test_batch_with_malformed_csv(self):
        """Test that batch processing handles malformed rows gracefully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["task_id", "target_identifier", "primary_metric", "secondary_metric"])
            writer.writeheader()
            writer.writerow({"task_id": "T1", "target_identifier": "K1", "primary_metric": "25.0", "secondary_metric": "10.0"})
            writer.writerow({"task_id": "T2", "target_identifier": "K2", "primary_metric": "INVALID", "secondary_metric": "5.0"})
            writer.writerow({"task_id": "T3", "target_identifier": "K3", "primary_metric": "15.0", "secondary_metric": "3.0"})
            temp_path = f.name

        try:
            from cli import main
            with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as out_f:
                out_path = out_f.name

            result = main(["batch", "-i", temp_path, "-o", out_path])
            assert result == 0

            with open(out_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            assert len(rows) == 3
            # The malformed row should have ERROR status
            error_rows = [r for r in rows if r.get("overall_urgency") == "ERROR"]
            assert len(error_rows) == 1
        finally:
            os.unlink(temp_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_batch_with_missing_fields(self):
        """Test that batch processing handles missing fields with defaults."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["task_id"])
            writer.writeheader()
            writer.writerow({"task_id": "T1"})
            temp_path = f.name

        try:
            from cli import main
            with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as out_f:
                out_path = out_f.name

            result = main(["batch", "-i", temp_path, "-o", out_path])
            assert result == 0

            with open(out_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            assert len(rows) == 1
        finally:
            os.unlink(temp_path)
            if os.path.exists(out_path):
                os.unlink(out_path)


class TestInputValidation:
    """Tests for input validation and sanitization."""

    def test_payload_with_extreme_values(self):
        """Test that extreme metric values are handled without crashing."""
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="EXTREME-01",
            target_identifier="KEY-01",
            primary_metric=float("1e10"),
            secondary_metric=float("1e10"),
            status_descriptor="NOMINAL",
        )
        dossier = supervisor.process_task(payload)
        # Extreme values should trigger elevated or critical urgency
        assert dossier.overall_urgency in (UrgencyLevel.ELEVATED, UrgencyLevel.CRITICAL_STAT)
        assert dossier.total_alerts > 0

    def test_payload_with_negative_values(self):
        """Test that negative metric values are handled."""
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="NEG-01",
            target_identifier="KEY-01",
            primary_metric=-5.0,
            secondary_metric=-2.0,
            status_descriptor="NOMINAL",
        )
        dossier = supervisor.process_task(payload)
        assert dossier.overall_urgency == UrgencyLevel.ROUTINE

    def test_payload_with_phi_in_task_id(self):
        """Test that PHI in task_id is rejected."""
        supervisor = SystemSupervisor(model_provider="mock")
        payload = SystemTaskPayload(
            task_id="Patient MRN-12345678",
            target_identifier="KEY-01",
            primary_metric=10.0,
            secondary_metric=5.0,
            status_descriptor="NOMINAL",
        )
        with pytest.raises(SecurityException):
            supervisor.process_task(payload)
