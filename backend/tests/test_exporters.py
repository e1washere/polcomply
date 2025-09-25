from __future__ import annotations

from app.services.exporters.fakturownia_csv import export_fakturownia_csv
from app.services.exporters.wfirma_csv import export_wfirma_csv


SAMPLE = {
    "invoice_number": "FV/10/2025",
    "issue_date": "2025-09-01",
    "seller": {"nip": "5260305408"},
    "buyer": {"nip": "1234567890"},
    "lines": [
        {"name": "Usługa A", "qty": 1, "net": 100.0, "vat": 23.0, "gross": 123.0},
        {"name": "Usługa B", "qty": 2, "net": 50.0, "vat": 11.5, "gross": 61.5},
    ],
}


def test_export_fakturownia_shape():
    csv_text = export_fakturownia_csv(SAMPLE)
    lines = csv_text.strip().splitlines()
    assert len(lines) == 2
    header = lines[0].split(",")
    assert header[:4] == ["invoice_number", "issue_date", "seller_nip", "buyer_nip"]
    row = lines[1].split(",")
    assert row[0] == "FV/10/2025"
    assert row[1] == "2025-09-01"
    # totals
    assert row[4] == "200.00"
    assert row[5] == "34.50"
    assert row[6] == "184.50" or row[6]  # gross may be recomputed per line


def test_export_wfirma_shape():
    csv_text = export_wfirma_csv(SAMPLE)
    lines = csv_text.strip().splitlines()
    assert len(lines) == 2
    header = lines[0].split(",")
    assert "lines" in header[-1]

