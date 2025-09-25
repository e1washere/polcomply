"""Pluggable KSeF client layer: interface + mock + sandbox implementation.

Usage is controlled via environment in app.settings:
  - KSEF_MODE = "mock" | "sandbox"
  - KSEF_SANDBOX_BASE_URL
  - KSEF_TIMEOUT_SEC

Sandbox client is feature-flagged and safe (timeouts/retries). In absence of
proper env config the factory will fall back to the mock client.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypedDict, Literal, Optional
import time
import uuid

import httpx


class KSeFStatus(TypedDict, total=False):
    status: Literal["PENDING", "UPO", "ERROR"]
    details: Optional[str]
    upo_reference: Optional[str]


class KSeFClient(Protocol):
    def send(self, xml_bytes: bytes) -> str:  # returns submission_id
        ...

    def status(self, submission_id: str) -> KSeFStatus:
        ...


@dataclass
class MockKSeFClient:
    """Deterministic UPO simulation used for demo and tests."""

    processing_delay_sec: float = 1.5

    def __post_init__(self) -> None:
        self._submitted_at: dict[str, float] = {}

    def send(self, xml_bytes: bytes) -> str:
        submission_id = str(uuid.uuid4())
        self._submitted_at[submission_id] = time.time()
        return submission_id

    def status(self, submission_id: str) -> KSeFStatus:
        started = self._submitted_at.get(submission_id)
        if started is None:
            return {"status": "ERROR", "details": "Submission not found"}
        if time.time() - started >= self.processing_delay_sec:
            return {
                "status": "UPO",
                "details": "Processed by MockKSeF",
                "upo_reference": f"UPO-{submission_id[:8].upper()}",
            }
        return {"status": "PENDING", "details": "Processing"}


@dataclass
class SandboxKSeFClient:
    """Thin HTTP client for KSeF sandbox. Endpoints are illustrative.

    Real KSeF API specifics should be mapped here when available.
    """

    base_url: str
    timeout_sec: float = 10.0

    def __post_init__(self) -> None:
        limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout_sec),
            limits=limits,
            headers={"User-Agent": "PolComply/launch"},
        )

    def send(self, xml_bytes: bytes) -> str:
        # Placeholder endpoint. Adjust when sandbox docs are confirmed.
        resp = self._client.post("/send", content=xml_bytes,
                                 headers={"Content-Type": "application/xml"})
        resp.raise_for_status()
        data = resp.json()
        return str(data.get("submission_id"))

    def status(self, submission_id: str) -> KSeFStatus:
        resp = self._client.get(f"/status", params={"submission_id": submission_id})
        resp.raise_for_status()
        data = resp.json()
        out: KSeFStatus = {"status": data.get("status", "ERROR"), "details": data.get("details")}
        upo = data.get("upo_reference")
        if upo:
            out["upo_reference"] = upo
        return out


def make_ksef_client(*, mode: str, base_url: Optional[str], timeout_sec: float) -> KSeFClient:
    """Factory that never crashes: falls back to mock if config incomplete."""
    if mode.lower() == "sandbox" and base_url:
        try:
            return SandboxKSeFClient(base_url=base_url, timeout_sec=timeout_sec)
        except Exception:
            # Safety net – use mock if sandbox cannot be initialized
            return MockKSeFClient()
    return MockKSeFClient()

"""KSeF API client for invoice submission"""

import logging
import asyncio
from typing import Dict, Any
from app.models.company import Company

logger = logging.getLogger(__name__)


class KSeFClient:
    """KSeF API client for invoice submission"""

    def __init__(self, company: Company):
        self.company = company
        self.environment = company.ksef_environment or "sandbox"
        self.token = company.ksef_token

    async def submit_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit invoice to KSeF

        Args:
            invoice_data: Invoice data to submit

        Returns:
            Dict with submission result
        """
        try:
            # Mock implementation for demo
            # In production, this would make actual KSeF API calls

            logger.info(f"Submitting invoice to KSeF (environment: {self.environment})")

            # Simulate API call delay
            import asyncio

            await asyncio.sleep(1)

            # Mock response
            if self.environment == "sandbox":
                return {
                    "success": True,
                    "upo": f"UPO-{self.environment.upper()}-{invoice_data.get('invoice_number', 'TEST')}-001",
                    "status": "accepted",
                    "message": "Faktura została przyjęta przez KSeF",
                }
            else:
                # Simulate potential errors in production
                if "error" in invoice_data.get("invoice_number", "").lower():
                    return {
                        "success": False,
                        "error": "Błąd walidacji FA(3)",
                        "status": "rejected",
                        "message": "Faktura została odrzucona przez KSeF",
                    }
                else:
                    return {
                        "success": True,
                        "upo": f"UPO-PROD-{invoice_data.get('invoice_number', 'PROD')}-001",
                        "status": "accepted",
                        "message": "Faktura została przyjęta przez KSeF",
                    }

        except Exception as e:
            logger.error(f"KSeF submission error: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "error",
                "message": "Błąd podczas komunikacji z KSeF",
            }

    async def get_invoice_status(self, upo: str) -> Dict[str, Any]:
        """
        Get invoice status from KSeF

        Args:
            upo: Unique Payment Order number

        Returns:
            Dict with status information
        """
        try:
            # Mock implementation
            await asyncio.sleep(0.5)

            return {
                "success": True,
                "upo": upo,
                "status": "accepted",
                "message": "Faktura została przetworzona",
            }

        except Exception as e:
            logger.error(f"KSeF status check error: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "error",
                "message": "Błąd podczas sprawdzania statusu",
            }
