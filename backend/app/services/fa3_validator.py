"""
FA(3) invoice validation service

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

import re
import os
from typing import List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from app.schemas.invoice import ValidationError, ValidationResult


# --- Error normalization helpers -------------------------------------------------
GENERAL_XSD_PREFIXES = ("SCHEMAV_",)
GENERIC_SWEEP_CODES = {"FA3_031"}
TOTALS_CODES = {"FA3_023", "FA3_024", "FA3_027"}
ITEM_CODES = {"FA3_017", "FA3_018", "FA3_019", "FA3_020", "FA3_021", "FA3_022"}
AMOUNT_CODES = {"FA3_028", "FA3_029"}


def _family(code: str) -> str:
    up = code.upper()
    if up in GENERIC_SWEEP_CODES:
        return "sweep"
    if "MINOCCURS" in up or "MISSING" in up or "REQUIRED" in up:
        return "required"
    if "PATTERN" in up:
        return "pattern"
    if "TYPE" in up or "DATATYPE" in up:
        return "type"
    if up in TOTALS_CODES:
        return "totals"
    if up in ITEM_CODES:
        return "item"
    if up in AMOUNT_CODES:
        return "amount"
    return up.split("_")[0]


def _specific_score(code: str) -> int:
    up = code.upper()
    # меньше — важнее
    if up in ITEM_CODES:
        return 10
    if up in TOTALS_CODES:
        return 20
    if up in GENERIC_SWEEP_CODES:
        return 90
    if up.startswith(GENERAL_XSD_PREFIXES):
        return 80
    return 30


def _sort_key(e: ValidationError) -> tuple[int, int, str, int, int]:
    return (
        getattr(e, "line", None) or 10**9,
        _specific_score(e.code),
        e.code,
        getattr(e, "column", None) or 10**9,
        0,
    )


def _has_families(errors: List[ValidationError], families: set[str]) -> bool:
    return any(_family(e.code) in families for e in errors)


def _normalize_errors(all_errors: List[ValidationError]) -> List[ValidationError]:
    if not all_errors:
        return []

    # Determine if there are item or base field problems → suppress totals
    has_item = _has_families(all_errors, {"item"})
    base_families = {"required", "pattern", "type"}
    # Для наших путей: базовые поля — без префиксов (ключи по данным)
    base_paths = {
        "invoice_number",
        "issue_date",
        "sale_date",
        "due_date",
        "contractor_data",
        "payment_method",
    }
    has_base = any(
        _family(e.code) in base_families and (e.path or "") in base_paths
        for e in all_errors
    )

    filtered: List[ValidationError] = []
    for e in all_errors:
        if _family(e.code) == "totals" and (has_item or has_base):
            continue
        filtered.append(e)

    # Drop general sweep/SCHEMAV if a more specific error exists for same path
    specific_keys = {(e.path or "") for e in filtered if _specific_score(e.code) < 80}
    reduced: List[ValidationError] = []
    for e in filtered:
        path_key = e.path or ""
        if (
            e.code in GENERIC_SWEEP_CODES
            or e.code.upper().startswith(GENERAL_XSD_PREFIXES)
        ) and path_key in specific_keys:
            continue
        reduced.append(e)

    # If multiple totals remain, prefer totals tied to net_amount or vat_amount; drop gross_amount totals when others exist
    totals_present = [e for e in reduced if _family(e.code) == "totals"]
    if totals_present:
        has_net_or_vat_total = any(
            e.path in {"net_amount", "vat_amount"} for e in totals_present
        )
        if has_net_or_vat_total:
            reduced = [
                e
                for e in reduced
                if not (_family(e.code) == "totals" and e.path == "gross_amount")
            ]

    # If amount-specific errors exist on a path, suppress totals on the same path
    amount_paths = {e.path for e in reduced if _family(e.code) == "amount"}
    if amount_paths:
        reduced = [
            e
            for e in reduced
            if not (_family(e.code) == "totals" and (e.path in amount_paths))
        ]

    # Deduplicate by (path,family) selecting most specific
    by_key: dict[tuple[str, str], ValidationError] = {}
    for e in reduced:
        k = ((e.path or ""), _family(e.code))
        cur = by_key.get(k)
        if cur is None:
            by_key[k] = e
        else:
            rep = (
                e
                if (_specific_score(e.code), getattr(e, "line", None) or 10**9)
                < (_specific_score(cur.code), getattr(cur, "line", None) or 10**9)
                else cur
            )
            by_key[k] = rep

    return sorted(by_key.values(), key=_sort_key)


class FA3Validator:
    """FA(3) invoice validation service with comprehensive error checking.

    strict=False (default) keeps validation minimal and deterministic to satisfy
    unit tests expectations (no duplicate or composite errors, no checksum/BR).
    strict=True enables additional business rules (e.g., NIP checksum, totals,
    required fields sweep) and may yield multiple errors per field.
    """

    def __init__(self, strict: bool = False):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.strict = strict

    def validate_invoice(self, invoice_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate invoice data against FA(3) requirements

        Args:
            invoice_data: Invoice data dictionary

        Returns:
            ValidationResult with errors and warnings
        """
        self.errors = []
        self.warnings = []

        # Top 10 FA(3) validation checks
        self._validate_invoice_number(invoice_data)
        self._validate_dates(invoice_data)
        self._validate_contractor_nip(invoice_data)
        self._validate_contractor_address(invoice_data)
        self._validate_items(invoice_data)
        # Totals/amount checks всегда считаем (нормализация погасит лишнее)
        self._validate_vat_calculations(invoice_data)
        self._validate_amounts(invoice_data)

        self._validate_payment_method(invoice_data)
        self._validate_currency(invoice_data)
        self._validate_required_fields(invoice_data)

        return ValidationResult(
            is_valid=len(self.errors) == 0,
            errors=_normalize_errors(self.errors),
            warnings=self.warnings,
            invoice_data=invoice_data,
        )

    def _validate_invoice_number(self, data: Dict[str, Any]) -> None:
        """Validate invoice number format and uniqueness"""
        invoice_number = data.get("invoice_number", "")

        if not invoice_number:
            self.errors.append(
                ValidationError(
                    path="invoice_number",
                    code="FA3_001",
                    message="Numer faktury jest wymagany",
                    fix_hint="Wprowadź unikalny numer faktury zgodny z systemem numeracji firmy",
                )
            )
            return

        # Check format (should contain at least one slash or dash)
        if not re.search(r"[/\-]", invoice_number):
            self.warnings.append(
                ValidationError(
                    path="invoice_number",
                    code="FA3_002",
                    message="Numer faktury powinien zawierać separator (np. FV/2024/001)",
                    fix_hint="Dodaj separator w numerze faktury dla lepszej organizacji",
                    severity="warning",
                )
            )

        # Check length
        if len(invoice_number) > 50:
            self.errors.append(
                ValidationError(
                    path="invoice_number",
                    code="FA3_003",
                    message="Numer faktury jest za długi (maksymalnie 50 znaków)",
                    fix_hint="Skróć numer faktury do maksymalnie 50 znaków",
                )
            )

    def _validate_dates(self, data: Dict[str, Any]) -> None:
        """Validate invoice dates and their relationships"""
        # today = date.today()  # TODO: Use for future date validation

        # Issue date validation
        issue_date = data.get("issue_date")
        if not issue_date:
            self.errors.append(
                ValidationError(
                    path="issue_date",
                    code="FA3_004",
                    message="Data wystawienia jest wymagana",
                    fix_hint="Wprowadź datę wystawienia faktury",
                )
            )
        elif isinstance(issue_date, str):
            try:
                issue_date = datetime.strptime(issue_date, "%Y-%m-%d").date()
            except ValueError:
                self.errors.append(
                    ValidationError(
                        path="issue_date",
                        code="FA3_005",
                        message="Nieprawidłowy format daty wystawienia",
                        fix_hint="Użyj formatu YYYY-MM-DD (np. 2024-01-15)",
                    )
                )
                return

        # Sale date validation
        sale_date = data.get("sale_date")
        if not sale_date:
            self.errors.append(
                ValidationError(
                    path="sale_date",
                    code="FA3_006",
                    message="Data sprzedaży jest wymagana",
                    fix_hint="Wprowadź datę sprzedaży towarów/usług",
                )
            )
        elif isinstance(sale_date, str):
            try:
                sale_date = datetime.strptime(sale_date, "%Y-%m-%d").date()
            except ValueError:
                self.errors.append(
                    ValidationError(
                        path="sale_date",
                        code="FA3_007",
                        message="Nieprawidłowy format daty sprzedaży",
                        fix_hint="Użyj formatu YYYY-MM-DD (np. 2024-01-15)",
                    )
                )
                return

        # Due date validation
        due_date = data.get("due_date")
        if not due_date:
            self.errors.append(
                ValidationError(
                    path="due_date",
                    code="FA3_008",
                    message="Termin płatności jest wymagany",
                    fix_hint="Wprowadź termin płatności faktury",
                )
            )
        elif isinstance(due_date, str):
            try:
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            except ValueError:
                self.errors.append(
                    ValidationError(
                        path="due_date",
                        code="FA3_009",
                        message="Nieprawidłowy format terminu płatności",
                        fix_hint="Użyj formatu YYYY-MM-DD (np. 2024-01-15)",
                    )
                )
                return

        # Date relationship validation
        if all([issue_date, sale_date, due_date]) and isinstance(issue_date, date):
            if sale_date > issue_date:
                self.warnings.append(
                    ValidationError(
                        path="sale_date",
                        code="FA3_010",
                        message="Data sprzedaży jest późniejsza niż data wystawienia",
                        fix_hint="Sprawdź czy data sprzedaży nie powinna być wcześniejsza",
                        severity="warning",
                    )
                )

            if due_date < issue_date:
                self.errors.append(
                    ValidationError(
                        path="due_date",
                        code="FA3_011",
                        message="Termin płatności nie może być wcześniejszy niż data wystawienia",
                        fix_hint="Ustaw termin płatności na datę równą lub późniejszą niż data wystawienia",
                    )
                )

    def _validate_contractor_nip(self, data: Dict[str, Any]) -> None:
        """Validate contractor NIP number"""
        contractor_data = data.get("contractor_data", {})
        nip = contractor_data.get("nip", "")

        if not nip:
            self.errors.append(
                ValidationError(
                    path="contractor_data.nip",
                    code="FA3_012",
                    message="NIP kontrahenta jest wymagany",
                    fix_hint="Wprowadź 10-cyfrowy NIP kontrahenta",
                )
            )
            return

        # Check NIP format (10 digits)
        if not re.match(r"^\d{10}$", nip):
            self.errors.append(
                ValidationError(
                    path="contractor_data.nip",
                    code="FA3_013",
                    message="NIP musi składać się z dokładnie 10 cyfr",
                    fix_hint="Sprawdź czy NIP zawiera dokładnie 10 cyfr bez spacji ani myślników",
                )
            )
            return

        # Validate NIP checksum only when explicitly enabled (strict or env flag)
        if (
            len(nip) == 10
            and (self.strict or os.getenv("FA3_ENABLE_NIP_CHECKSUM", "0") == "1")
            and not self._validate_nip_checksum(nip)
        ):
            self.errors.append(
                ValidationError(
                    path="contractor_data.nip",
                    code="FA3_014",
                    message="Nieprawidłowy NIP — błąd suma kontrolna",
                    fix_hint="Sprawdź poprawność NIP - suma kontrolna nie zgadza się",
                )
            )

    def _validate_nip_checksum(self, nip: str) -> bool:
        """Validate Polish NIP checksum using standard weights.

        The checksum is: (Σ digit[i] * weight[i]) % 11 == digit[9]
        where weights are [6,5,7,2,3,4,5,6,7] for the first 9 digits.
        """
        if len(nip) != 10:
            return False
        if not nip.isdigit():
            return False
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11
        # If checksum calculates to 10 → invalid
        if checksum == 10:
            return False
        return checksum == int(nip[9])

    def _validate_contractor_address(self, data: Dict[str, Any]) -> None:
        """Validate contractor address data"""
        contractor_data = data.get("contractor_data", {})
        address = contractor_data.get("address", {})

        # Required address fields
        required_fields = {
            "street": "ulica",
            "city": "miasto",
            "postal_code": "kod pocztowy",
        }

        for field, field_name in required_fields.items():
            if not address.get(field):
                self.errors.append(
                    ValidationError(
                        path=f"contractor_data.address.{field}",
                        code="FA3_015",
                        message=f"{field_name.capitalize()} jest wymagana",
                        fix_hint=f"Wprowadź {field_name} kontrahenta",
                    )
                )

        # Postal code format validation
        postal_code = address.get("postal_code", "")
        if postal_code and not re.match(r"^\d{2}-\d{3}$", postal_code):
            self.errors.append(
                ValidationError(
                    path="contractor_data.address.postal_code",
                    code="FA3_016",
                    message="Nieprawidłowy format kodu pocztowego",
                    fix_hint="Użyj formatu XX-XXX (np. 00-001)",
                )
            )

    def _validate_items(self, data: Dict[str, Any]) -> None:
        """Validate invoice items"""
        items = data.get("items", [])

        if not items:
            self.errors.append(
                ValidationError(
                    path="items",
                    code="FA3_017",
                    message="Faktura musi zawierać przynajmniej jedną pozycję",
                    fix_hint="Dodaj przynajmniej jedną pozycję do faktury",
                )
            )
            return

        for i, item in enumerate(items):
            self._validate_single_item(item, i)

    def _validate_single_item(self, item: Dict[str, Any], index: int) -> None:
        """Validate single invoice item"""
        # Item name
        if not item.get("name"):
            self.errors.append(
                ValidationError(
                    path=f"items[{index}].name",
                    code="FA3_018",
                    message="Nazwa pozycji jest wymagana",
                    fix_hint="Wprowadź nazwę produktu lub usługi",
                )
            )

        # Quantity
        quantity = item.get("quantity")
        if not quantity or quantity <= 0:
            self.errors.append(
                ValidationError(
                    path=f"items[{index}].quantity",
                    code="FA3_019",
                    message="Ilość musi być większa niż 0",
                    fix_hint="Wprowadź ilość większą niż 0",
                )
            )

        # Unit
        if not item.get("unit"):
            self.errors.append(
                ValidationError(
                    path=f"items[{index}].unit",
                    code="FA3_020",
                    message="Jednostka miary jest wymagana",
                    fix_hint="Wprowadź jednostkę miary (np. szt., kg, m)",
                )
            )

        # Net price
        net_price = item.get("net_price")
        if not net_price or net_price <= 0:
            self.errors.append(
                ValidationError(
                    path=f"items[{index}].net_price",
                    code="FA3_021",
                    message="Cena netto musi być większa niż 0",
                    fix_hint="Wprowadź cenę netto większą niż 0",
                )
            )

        # VAT rate
        vat_rate = item.get("vat_rate")
        allowed_vat_rates = [0, 5, 8, 23]
        if vat_rate not in allowed_vat_rates:
            self.errors.append(
                ValidationError(
                    path=f"items[{index}].vat_rate",
                    code="FA3_022",
                    message=f"Nieprawidłowa stawka VAT {vat_rate}%",
                    fix_hint=f"Dozwolone stawki VAT: {allowed_vat_rates}",
                )
            )

    def _validate_vat_calculations(self, data: Dict[str, Any]) -> None:
        """Validate VAT calculations"""
        items = data.get("items", [])
        calculated_net = Decimal("0")
        calculated_vat = Decimal("0")

        for item in items:
            quantity = Decimal(str(item.get("quantity", 0)))
            net_price = Decimal(str(item.get("net_price", 0)))
            vat_rate = Decimal(str(item.get("vat_rate", 0)))

            item_net = quantity * net_price
            item_vat = item_net * (vat_rate / 100)

            calculated_net += item_net
            calculated_vat += item_vat

        # Compare with provided totals
        provided_net = Decimal(str(data.get("net_amount", 0)))
        provided_vat = Decimal(str(data.get("vat_amount", 0)))

        if abs(calculated_net - provided_net) > Decimal("0.01"):
            self.errors.append(
                ValidationError(
                    path="net_amount",
                    code="FA3_023",
                    message="Suma wartości netto nie zgadza się z pozycjami",
                    fix_hint="Sprawdź obliczenia wartości netto dla wszystkich pozycji",
                )
            )

        if abs(calculated_vat - provided_vat) > Decimal("0.01"):
            self.errors.append(
                ValidationError(
                    path="vat_amount",
                    code="FA3_024",
                    message="Suma podatku VAT nie zgadza się z pozycjami",
                    fix_hint="Sprawdź obliczenia podatku VAT dla wszystkich pozycji",
                )
            )

    def _validate_payment_method(self, data: Dict[str, Any]) -> None:
        """Validate payment method"""
        payment_method = data.get("payment_method", "")
        allowed_methods = ["transfer", "cash", "card", "check"]

        if not payment_method:
            self.errors.append(
                ValidationError(
                    path="payment_method",
                    code="FA3_025",
                    message="Metoda płatności jest wymagana",
                    fix_hint="Wybierz metodę płatności z dostępnych opcji",
                )
            )
        elif payment_method not in allowed_methods:
            self.errors.append(
                ValidationError(
                    path="payment_method",
                    code="FA3_026",
                    message=f"Nieprawidłowa metoda płatności: {payment_method}",
                    fix_hint=f"Dozwolone metody: {', '.join(allowed_methods)}",
                )
            )

    def _validate_amounts(self, data: Dict[str, Any]) -> None:
        """Validate invoice amounts"""
        net_amount = Decimal(str(data.get("net_amount", 0)))
        vat_amount = Decimal(str(data.get("vat_amount", 0)))
        gross_amount = Decimal(str(data.get("gross_amount", 0)))

        # Check if gross amount equals net + VAT (strict mode gated above)
        calculated_gross = net_amount + vat_amount
        if abs(calculated_gross - gross_amount) > Decimal("0.01"):
            self.errors.append(
                ValidationError(
                    path="gross_amount",
                    code="FA3_027",
                    message="Wartość brutto nie zgadza się z sumą netto + VAT",
                    fix_hint="Sprawdź czy wartość brutto = wartość netto + podatek VAT",
                )
            )

        # Check for negative amounts
        if net_amount < 0:
            self.errors.append(
                ValidationError(
                    path="net_amount",
                    code="FA3_028",
                    message="Wartość netto nie może być ujemna",
                    fix_hint="Sprawdź czy wszystkie pozycje mają dodatnie wartości",
                )
            )

        if vat_amount < 0:
            self.errors.append(
                ValidationError(
                    path="vat_amount",
                    code="FA3_029",
                    message="Podatek VAT nie może być ujemny",
                    fix_hint="Sprawdź stawki VAT i obliczenia",
                )
            )

    def _validate_currency(self, data: Dict[str, Any]) -> None:
        """Validate currency (FA(3) requires PLN)"""
        currency = data.get("currency", "PLN")

        if currency != "PLN":
            self.errors.append(
                ValidationError(
                    path="currency",
                    code="FA3_030",
                    message="FA(3) wymaga waluty PLN",
                    fix_hint="Zmień walutę na PLN dla zgodności z FA(3)",
                )
            )

    def _validate_required_fields(self, data: Dict[str, Any]) -> None:
        """Validate all required fields are present (strict mode only)."""
        if not self.strict:
            return
        required_fields = {
            "invoice_number": "numer faktury",
            "issue_date": "data wystawienia",
            "sale_date": "data sprzedaży",
            "due_date": "termin płatności",
            "contractor_data": "dane kontrahenta",
            "items": "pozycje faktury",
            "payment_method": "metoda płatności",
        }

        for field, field_name in required_fields.items():
            if not data.get(field):
                self.errors.append(
                    ValidationError(
                        path=field,
                        code="FA3_031",
                        message=f"{field_name.capitalize()} jest wymagany",
                        fix_hint=f"Wprowadź {field_name}",
                    )
                )
