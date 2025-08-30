"""FA(3) invoice validation service"""

import re
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal
from app.schemas.invoice import ValidationError, ValidationResult, InvoiceCreate


class FA3Validator:
    """FA(3) invoice validation service with comprehensive error checking"""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
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
        self._validate_vat_calculations(invoice_data)
        self._validate_payment_method(invoice_data)
        self._validate_amounts(invoice_data)
        self._validate_currency(invoice_data)
        self._validate_required_fields(invoice_data)
        
        return ValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
            invoice_data=invoice_data
        )
    
    def _validate_invoice_number(self, data: Dict[str, Any]) -> None:
        """Validate invoice number format and uniqueness"""
        invoice_number = data.get('invoice_number', '')
        
        if not invoice_number:
            self.errors.append(ValidationError(
                path="invoice_number",
                code="FA3_001",
                message="Numer faktury jest wymagany",
                fix_hint="Wprowadź unikalny numer faktury zgodny z systemem numeracji firmy"
            ))
            return
        
        # Check format (should contain at least one slash or dash)
        if not re.search(r'[/\-]', invoice_number):
            self.warnings.append(ValidationError(
                path="invoice_number",
                code="FA3_002",
                message="Numer faktury powinien zawierać separator (np. FV/2024/001)",
                fix_hint="Dodaj separator w numerze faktury dla lepszej organizacji",
                severity="warning"
            ))
        
        # Check length
        if len(invoice_number) > 50:
            self.errors.append(ValidationError(
                path="invoice_number",
                code="FA3_003",
                message="Numer faktury jest za długi (maksymalnie 50 znaków)",
                fix_hint="Skróć numer faktury do maksymalnie 50 znaków"
            ))
    
    def _validate_dates(self, data: Dict[str, Any]) -> None:
        """Validate invoice dates and their relationships"""
        today = date.today()
        
        # Issue date validation
        issue_date = data.get('issue_date')
        if not issue_date:
            self.errors.append(ValidationError(
                path="issue_date",
                code="FA3_004",
                message="Data wystawienia jest wymagana",
                fix_hint="Wprowadź datę wystawienia faktury"
            ))
        elif isinstance(issue_date, str):
            try:
                issue_date = datetime.strptime(issue_date, "%Y-%m-%d").date()
            except ValueError:
                self.errors.append(ValidationError(
                    path="issue_date",
                    code="FA3_005",
                    message="Nieprawidłowy format daty wystawienia",
                    fix_hint="Użyj formatu YYYY-MM-DD (np. 2024-01-15)"
                ))
                return
        
        # Sale date validation
        sale_date = data.get('sale_date')
        if not sale_date:
            self.errors.append(ValidationError(
                path="sale_date",
                code="FA3_006",
                message="Data sprzedaży jest wymagana",
                fix_hint="Wprowadź datę sprzedaży towarów/usług"
            ))
        elif isinstance(sale_date, str):
            try:
                sale_date = datetime.strptime(sale_date, "%Y-%m-%d").date()
            except ValueError:
                self.errors.append(ValidationError(
                    path="sale_date",
                    code="FA3_007",
                    message="Nieprawidłowy format daty sprzedaży",
                    fix_hint="Użyj formatu YYYY-MM-DD (np. 2024-01-15)"
                ))
                return
        
        # Due date validation
        due_date = data.get('due_date')
        if not due_date:
            self.errors.append(ValidationError(
                path="due_date",
                code="FA3_008",
                message="Termin płatności jest wymagany",
                fix_hint="Wprowadź termin płatności faktury"
            ))
        elif isinstance(due_date, str):
            try:
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            except ValueError:
                self.errors.append(ValidationError(
                    path="due_date",
                    code="FA3_009",
                    message="Nieprawidłowy format terminu płatności",
                    fix_hint="Użyj formatu YYYY-MM-DD (np. 2024-01-15)"
                ))
                return
        
        # Date relationship validation
        if all([issue_date, sale_date, due_date]) and isinstance(issue_date, date):
            if sale_date > issue_date:
                self.warnings.append(ValidationError(
                    path="sale_date",
                    code="FA3_010",
                    message="Data sprzedaży jest późniejsza niż data wystawienia",
                    fix_hint="Sprawdź czy data sprzedaży nie powinna być wcześniejsza",
                    severity="warning"
                ))
            
            if due_date < issue_date:
                self.errors.append(ValidationError(
                    path="due_date",
                    code="FA3_011",
                    message="Termin płatności nie może być wcześniejszy niż data wystawienia",
                    fix_hint="Ustaw termin płatności na datę równą lub późniejszą niż data wystawienia"
                ))
    
    def _validate_contractor_nip(self, data: Dict[str, Any]) -> None:
        """Validate contractor NIP number"""
        contractor_data = data.get('contractor_data', {})
        nip = contractor_data.get('nip', '')
        
        if not nip:
            self.errors.append(ValidationError(
                path="contractor_data.nip",
                code="FA3_012",
                message="NIP kontrahenta jest wymagany",
                fix_hint="Wprowadź 10-cyfrowy NIP kontrahenta"
            ))
            return
        
        # Check NIP format (10 digits)
        if not re.match(r'^\d{10}$', nip):
            self.errors.append(ValidationError(
                path="contractor_data.nip",
                code="FA3_013",
                message="NIP musi składać się z dokładnie 10 cyfr",
                fix_hint="Sprawdź czy NIP zawiera dokładnie 10 cyfr bez spacji ani myślników"
            ))
            return
        
        # Validate NIP checksum (Polish NIP validation algorithm)
        if not self._validate_nip_checksum(nip):
            self.errors.append(ValidationError(
                path="contractor_data.nip",
                code="FA3_014",
                message="Nieprawidłowy NIP - błąd w sumie kontrolnej",
                fix_hint="Sprawdź poprawność NIP - suma kontrolna nie zgadza się"
            ))
    
    def _validate_nip_checksum(self, nip: str) -> bool:
        """Validate Polish NIP checksum"""
        if len(nip) != 10:
            return False
        
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9))
        checksum %= 11
        
        return checksum == int(nip[9])
    
    def _validate_contractor_address(self, data: Dict[str, Any]) -> None:
        """Validate contractor address data"""
        contractor_data = data.get('contractor_data', {})
        address = contractor_data.get('address', {})
        
        # Required address fields
        required_fields = {
            'street': 'ulica',
            'city': 'miasto',
            'postal_code': 'kod pocztowy'
        }
        
        for field, field_name in required_fields.items():
            if not address.get(field):
                self.errors.append(ValidationError(
                    path=f"contractor_data.address.{field}",
                    code=f"FA3_015",
                    message=f"{field_name.capitalize()} jest wymagana",
                    fix_hint=f"Wprowadź {field_name} kontrahenta"
                ))
        
        # Postal code format validation
        postal_code = address.get('postal_code', '')
        if postal_code and not re.match(r'^\d{2}-\d{3}$', postal_code):
            self.errors.append(ValidationError(
                path="contractor_data.address.postal_code",
                code="FA3_016",
                message="Nieprawidłowy format kodu pocztowego",
                fix_hint="Użyj formatu XX-XXX (np. 00-001)"
            ))
    
    def _validate_items(self, data: Dict[str, Any]) -> None:
        """Validate invoice items"""
        items = data.get('items', [])
        
        if not items:
            self.errors.append(ValidationError(
                path="items",
                code="FA3_017",
                message="Faktura musi zawierać przynajmniej jedną pozycję",
                fix_hint="Dodaj przynajmniej jedną pozycję do faktury"
            ))
            return
        
        for i, item in enumerate(items):
            self._validate_single_item(item, i)
    
    def _validate_single_item(self, item: Dict[str, Any], index: int) -> None:
        """Validate single invoice item"""
        # Item name
        if not item.get('name'):
            self.errors.append(ValidationError(
                path=f"items[{index}].name",
                code="FA3_018",
                message="Nazwa pozycji jest wymagana",
                fix_hint="Wprowadź nazwę produktu lub usługi"
            ))
        
        # Quantity
        quantity = item.get('quantity')
        if not quantity or quantity <= 0:
            self.errors.append(ValidationError(
                path=f"items[{index}].quantity",
                code="FA3_019",
                message="Ilość musi być większa niż 0",
                fix_hint="Wprowadź ilość większą niż 0"
            ))
        
        # Unit
        if not item.get('unit'):
            self.errors.append(ValidationError(
                path=f"items[{index}].unit",
                code="FA3_020",
                message="Jednostka miary jest wymagana",
                fix_hint="Wprowadź jednostkę miary (np. szt., kg, m)"
            ))
        
        # Net price
        net_price = item.get('net_price')
        if not net_price or net_price <= 0:
            self.errors.append(ValidationError(
                path=f"items[{index}].net_price",
                code="FA3_021",
                message="Cena netto musi być większa niż 0",
                fix_hint="Wprowadź cenę netto większą niż 0"
            ))
        
        # VAT rate
        vat_rate = item.get('vat_rate')
        allowed_vat_rates = [0, 5, 8, 23]
        if vat_rate not in allowed_vat_rates:
            self.errors.append(ValidationError(
                path=f"items[{index}].vat_rate",
                code="FA3_022",
                message=f"Nieprawidłowa stawka VAT {vat_rate}%",
                fix_hint=f"Dozwolone stawki VAT: {allowed_vat_rates}"
            ))
    
    def _validate_vat_calculations(self, data: Dict[str, Any]) -> None:
        """Validate VAT calculations"""
        items = data.get('items', [])
        calculated_net = Decimal('0')
        calculated_vat = Decimal('0')
        
        for item in items:
            quantity = Decimal(str(item.get('quantity', 0)))
            net_price = Decimal(str(item.get('net_price', 0)))
            vat_rate = Decimal(str(item.get('vat_rate', 0)))
            
            item_net = quantity * net_price
            item_vat = item_net * (vat_rate / 100)
            
            calculated_net += item_net
            calculated_vat += item_vat
        
        # Compare with provided totals
        provided_net = Decimal(str(data.get('net_amount', 0)))
        provided_vat = Decimal(str(data.get('vat_amount', 0)))
        
        if abs(calculated_net - provided_net) > Decimal('0.01'):
            self.errors.append(ValidationError(
                path="net_amount",
                code="FA3_023",
                message="Suma wartości netto nie zgadza się z pozycjami",
                fix_hint="Sprawdź obliczenia wartości netto dla wszystkich pozycji"
            ))
        
        if abs(calculated_vat - provided_vat) > Decimal('0.01'):
            self.errors.append(ValidationError(
                path="vat_amount",
                code="FA3_024",
                message="Suma podatku VAT nie zgadza się z pozycjami",
                fix_hint="Sprawdź obliczenia podatku VAT dla wszystkich pozycji"
            ))
    
    def _validate_payment_method(self, data: Dict[str, Any]) -> None:
        """Validate payment method"""
        payment_method = data.get('payment_method', '')
        allowed_methods = ['transfer', 'cash', 'card', 'check']
        
        if not payment_method:
            self.errors.append(ValidationError(
                path="payment_method",
                code="FA3_025",
                message="Metoda płatności jest wymagana",
                fix_hint="Wybierz metodę płatności z dostępnych opcji"
            ))
        elif payment_method not in allowed_methods:
            self.errors.append(ValidationError(
                path="payment_method",
                code="FA3_026",
                message=f"Nieprawidłowa metoda płatności: {payment_method}",
                fix_hint=f"Dozwolone metody: {', '.join(allowed_methods)}"
            ))
    
    def _validate_amounts(self, data: Dict[str, Any]) -> None:
        """Validate invoice amounts"""
        net_amount = Decimal(str(data.get('net_amount', 0)))
        vat_amount = Decimal(str(data.get('vat_amount', 0)))
        gross_amount = Decimal(str(data.get('gross_amount', 0)))
        
        # Check if gross amount equals net + VAT
        calculated_gross = net_amount + vat_amount
        if abs(calculated_gross - gross_amount) > Decimal('0.01'):
            self.errors.append(ValidationError(
                path="gross_amount",
                code="FA3_027",
                message="Wartość brutto nie zgadza się z sumą netto + VAT",
                fix_hint="Sprawdź czy wartość brutto = wartość netto + podatek VAT"
            ))
        
        # Check for negative amounts
        if net_amount < 0:
            self.errors.append(ValidationError(
                path="net_amount",
                code="FA3_028",
                message="Wartość netto nie może być ujemna",
                fix_hint="Sprawdź czy wszystkie pozycje mają dodatnie wartości"
            ))
        
        if vat_amount < 0:
            self.errors.append(ValidationError(
                path="vat_amount",
                code="FA3_029",
                message="Podatek VAT nie może być ujemny",
                fix_hint="Sprawdź stawki VAT i obliczenia"
            ))
    
    def _validate_currency(self, data: Dict[str, Any]) -> None:
        """Validate currency (FA(3) requires PLN)"""
        currency = data.get('currency', 'PLN')
        
        if currency != 'PLN':
            self.errors.append(ValidationError(
                path="currency",
                code="FA3_030",
                message="FA(3) wymaga waluty PLN",
                fix_hint="Zmień walutę na PLN dla zgodności z FA(3)"
            ))
    
    def _validate_required_fields(self, data: Dict[str, Any]) -> None:
        """Validate all required fields are present"""
        required_fields = {
            'invoice_number': 'numer faktury',
            'issue_date': 'data wystawienia',
            'sale_date': 'data sprzedaży',
            'due_date': 'termin płatności',
            'contractor_data': 'dane kontrahenta',
            'items': 'pozycje faktury',
            'payment_method': 'metoda płatności'
        }
        
        for field, field_name in required_fields.items():
            if not data.get(field):
                self.errors.append(ValidationError(
                    path=field,
                    code="FA3_031",
                    message=f"{field_name.capitalize()} jest wymagany",
                    fix_hint=f"Wprowadź {field_name}"
                ))
