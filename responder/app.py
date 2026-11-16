from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException


BACKEND_URL = os.getenv("PULSELINK_BACKEND_URL", "http://backend:8000")
REPORT_SECRET = os.getenv("RESPONDER_SHARED_SECRET")
app = FastAPI(title="PulseLink Responder", version="1.0.0")


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


async def collect_evidence(client: httpx.AsyncClient) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    for name, path in (("health", "/health"), ("readiness", "/ready"), ("metrics", "/metrics")):
        try:
            response = await client.get(f"{BACKEND_URL}{path}")
            evidence[name] = {"status_code": response.status_code, "body": response.text[:4000]}
        except httpx.HTTPError as exc:
            evidence[name] = {"error": type(exc).__name__}
    return evidence


def diagnose(alert: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    name = alert.get("labels", {}).get("alertname", "UnknownAlert")
    if name == "RedirectFailureRateHigh":
        return {
            "hypothesis": "User-facing redirect failures are above the error budget; inspect the latest deployment and dependencies.",
            "confidence": "medium",
            "recommended_action": "human_approved_rollback_or_dependency_recovery",
            "safe_action": "evidence_collected_and_recovery_check_scheduled",
        }
    if name == "RedirectLatencyHigh":
        return {
            "hypothesis": "Redirect latency is degrading while users can still reach the service.",
            "confidence": "medium",
            "recommended_action": "inspect_dependency_latency_and_scale_or_rollback_with_approval",
            "safe_action": "evidence_collected_and_recovery_check_scheduled",
        }
    if name == "RedirectTrafficMissing":
        return {
            "hypothesis": "Redirect telemetry stopped; the service or telemetry path may be unavailable.",
            "confidence": "low",
            "recommended_action": "human_approved_service_restart_or_rollback",
            "safe_action": "health_and_readiness_rechecked",
        }
    return {
        "hypothesis": "Unrecognized alert requires human investigation.",
        "confidence": "low",
        "recommended_action": "human_investigation",
        "safe_action": "evidence_collected",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/alerts", status_code=202)
async def receive_alert(payload: dict[str, Any]) -> dict[str, Any]:
    alerts = payload.get("alerts")
    if not isinstance(alerts, list):
        raise HTTPException(status_code=422, detail="Alert payload must contain alerts")
    reports = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        for alert in alerts:
            evidence = await collect_evidence(client)
            report = {
                "incident_id": alert.get("fingerprint") or f"incident-{timestamp()}",
                "alert_status": payload.get("status", "firing"),
                "alert": {"labels": alert.get("labels", {}), "annotations": alert.get("annotations", {})},
                "evidence": evidence,
                "diagnosis": diagnose(alert, evidence),
                "agent": "pulselink-responder",
                "created_at": timestamp(),
                "action_status": "proposed",
            }
            headers = {"x-responder-secret": REPORT_SECRET} if REPORT_SECRET else {}
            try:
                response = await client.post(f"{BACKEND_URL}/internal/responder/reports", json=report, headers=headers)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise HTTPException(status_code=502, detail="Incident report delivery failed") from exc
            reports.append(report["incident_id"])
    return {"accepted": len(reports), "reports": reports}
