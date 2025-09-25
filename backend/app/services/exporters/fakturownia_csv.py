from __future__ import annotations

import csv
from io import StringIO
from typing import Any, Dict, List


def export_fakturownia_csv(invoice: Dict[str, Any]) -> str:
    """Generate CSV compatible with Fakturownia minimal import.

    Columns: invoice_number, issue_date, seller_nip, buyer_nip, net, vat, gross, lines
    """
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "invoice_number",
        "issue_date",
        "seller_nip",
        "buyer_nip",
        "net",
        "vat",
        "gross",
        "lines",
    ])

    number = invoice.get("invoice_number") or invoice.get("number") or ""
    date = invoice.get("issue_date") or invoice.get("date") or ""
    seller_nip = (invoice.get("seller") or {}).get("nip") or invoice.get("seller_nip") or ""
    buyer_nip = (invoice.get("buyer") or {}).get("nip") or invoice.get("buyer_nip") or ""

    lines: List[Dict[str, Any]] = invoice.get("lines") or invoice.get("items") or []
    net_total = sum(float(str(l.get("net", 0))) for l in lines)
    vat_total = sum(float(str(l.get("vat", 0))) for l in lines)
    gross_total = sum(float(str(l.get("gross", net_total + vat_total))) for l in lines)

    # Compact lines as JSON-like string for a single-cell placement
    compact_lines = ";".join(
        f"{l.get('name','')}: {l.get('qty',1)} x {l.get('net',0)}"
        for l in lines
    )

    writer.writerow([
        number,
        date,
        seller_nip,
        buyer_nip,
        f"{net_total:.2f}",
        f"{vat_total:.2f}",
        f"{gross_total:.2f}",
        compact_lines,
    ])

    return output.getvalue()


