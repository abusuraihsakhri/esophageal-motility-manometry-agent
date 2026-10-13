"use strict";

/*
 * Offline demonstration of the three generic rule thresholds in agents/workers.py.
 * This is not an implementation of Chicago Classification v4.0 or a clinical tool.
 */
function evaluateDemo(input) {
  const primary = Number(input.primary_metric);
  const secondary = Number(input.secondary_metric);
  if (![primary, secondary].every(Number.isFinite)) {
    throw new Error("Measurements must be finite numbers.");
  }
  const status = String(input.status_descriptor || "NOMINAL").toUpperCase();
  const critical = input.is_critical_flag === true;
  const alerts = [];

  if (primary > 25) {
    alerts.push({
      worker: "InvariantQCWorker",
      urgency: "ELEVATED_RISK",
      summary: "Primary metric above demonstration threshold (25)",
    });
  }
  if (critical || secondary > 12) {
    alerts.push({
      worker: "SafetyEscalationWorker",
      urgency: critical ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      summary: critical ? "Manual critical flag set" : "Secondary metric above demonstration threshold (12)",
    });
  }
  if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"].some(word => status.includes(word))) {
    alerts.push({
      worker: "ProtocolConformanceWorker",
      urgency: "ELEVATED_RISK",
      summary: "Descriptor keyword flag",
    });
  }
  const criticalCount = alerts.filter(a => a.urgency === "CRITICAL_STAT_PANIC").length;
  const overall = criticalCount ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK" : "ROUTINE";
  return {
    mode: "LOCAL_RULE_DEMONSTRATION",
    clinical_classification: "NOT_PERFORMED",
    task_id: String(input.task_id),
    target_identifier: String(input.target_identifier),
    overall_urgency: overall,
    integrity_status: criticalCount ? "RECALIBRATION_REQUIRED" : alerts.length ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
    total_alerts: alerts.length,
    critical_alerts_count: criticalCount,
    alerts,
    signed_audit_trail: false,
    note: "Generic demonstration thresholds, not validated HRM reference limits, diagnosis, or a clinical recommendation.",
  };
}

function initializeDemo() {
  const form = document.getElementById("audit-form");
  const result = document.getElementById("result");
  const error = document.getElementById("error");
  const summary = document.getElementById("result-summary");
  const download = document.getElementById("download");
  let lastResult = null;

  form.addEventListener("submit", event => {
    event.preventDefault();
    error.textContent = "";
    download.disabled = true;
    lastResult = null;
    const field = id => document.getElementById(id).value.trim();
    const primaryText = field("primary_metric");
    const secondaryText = field("secondary_metric");
    const taskId = field("task_id");
    const targetId = field("target_id");
    const descriptor = field("status_descriptor");
    const prohibited = /(?:\b\d{3}-\d{2}-\d{4}\b|\b(?:MRN|DOB|SSN)\s*[:#-]?\s*\w+|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})/i;
    if (!taskId || !targetId || !descriptor || !primaryText || !secondaryText) {
      error.textContent = "All fields are required.";
      return;
    }
    if ([taskId, targetId, descriptor].some(s => prohibited.test(s))) {
      error.textContent = "Use synthetic identifiers only. Recognizable personal identifiers are not accepted.";
      return;
    }
    try {
      const output = evaluateDemo({
        task_id: taskId, target_identifier: targetId,
        primary_metric: primaryText, secondary_metric: secondaryText,
        status_descriptor: descriptor,
        is_critical_flag: document.getElementById("is_critical").checked,
      });
      lastResult = output;
      summary.textContent = output.overall_urgency + " · " + output.total_alerts + " rule alert(s)";
      result.textContent = JSON.stringify(output, null, 2);
      download.disabled = false;
    } catch (err) {
      error.textContent = err.message;
    }
  });

  download.addEventListener("click", () => {
    if (!lastResult) return;
    const blob = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "manometry-rule-demo.json";
    link.click();
    URL.revokeObjectURL(url);
  });
}
if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", initializeDemo);
}
if (typeof module !== "undefined" && module.exports) {
  module.exports = { evaluateDemo };
}
