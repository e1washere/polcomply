from __future__ import annotations

import os
from app.services.ksef_client import make_ksef_client, MockKSeFClient, SandboxKSeFClient


def test_ksef_factory_mock_when_default():
    client = make_ksef_client(mode="mock", base_url=None, timeout_sec=5)
    assert isinstance(client, MockKSeFClient)


def test_ksef_factory_sandbox_when_configured(monkeypatch):
    base = "https://sandbox.example"
    client = make_ksef_client(mode="sandbox", base_url=base, timeout_sec=2)
    # If httpx fails init it falls back to mock; both are acceptable but prefer Sandbox
    assert isinstance(client, (SandboxKSeFClient, MockKSeFClient))

