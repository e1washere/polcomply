"""Tests for validation API endpoint"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile

from app.main import app

client = TestClient(app)


def test_validate_xml_valid():
    """Test validation with valid XML"""
    
    valid_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<Faktura xmlns="http://crd.gov.pl/wzor/2023/06/21/12348/">
    <Naglowek>
        <KodFormularza>
            <Kod>FA</Kod>
            <WersjaSchemy>1-0E</WersjaSchemy>
        </KodFormularza>
        <WariantFormularza>1</WariantFormularza>
        <DataWystawienia>2024-01-15</DataWystawienia>
        <MiejsceWystawienia>Warszawa</MiejsceWystawienia>
        <DataSprzedazy>2024-01-15</DataSprzedazy>
        <KodWaluty>PLN</KodWaluty>
        <P_1>FV/2024/001</P_1>
        <P_2>FV/2024/001</P_2>
    </Naglowek>
    <Sprzedawca>
        <DaneIdentyfikacyjne>
            <NIP>5262312345</NIP>
            <Nazwa>Test Company</Nazwa>
        </DaneIdentyfikacyjne>
        <Adres>
            <KodKraju>PL</KodKraju>
            <Miejscowosc>Warszawa</Miejscowosc>
            <KodPocztowy>00-001</KodPocztowy>
            <Poczta>Warszawa</Poczta>
        </Adres>
    </Sprzedawca>
    <Nabywca>
        <DaneIdentyfikacyjne>
            <NIP>7792439665</NIP>
            <Nazwa>Client Company</Nazwa>
        </DaneIdentyfikacyjne>
        <Adres>
            <KodKraju>PL</KodKraju>
            <Miejscowosc>Krakow</Miejscowosc>
            <KodPocztowy>30-001</KodPocztowy>
            <Poczta>Krakow</Poczta>
        </Adres>
    </Nabywca>
    <Pozycje>
        <Pozycja>
            <LpSprzedazy>1</LpSprzedazy>
            <Nazwa>Test Product</Nazwa>
            <Miara>szt.</Miara>
            <Ilosc>2</Ilosc>
            <CenaJednostkowa>100.00</CenaJednostkowa>
            <WartoscNetto>200.00</WartoscNetto>
            <StawkaPodatku>23</StawkaPodatku>
            <KwotaPodatku>46.00</KwotaPodatku>
            <WartoscBrutto>246.00</WartoscBrutto>
        </Pozycja>
    </Pozycje>
    <Podsumowanie>
        <LiczbaPozycji>1</LiczbaPozycji>
        <WartoscNetto>200.00</WartoscNetto>
        <KwotaPodatku>46.00</KwotaPodatku>
        <WartoscBrutto>246.00</WartoscBrutto>
    </Podsumowanie>
</Faktura>"""

        response = client.post(
        "/api/validate/xml",
        files={"file": ("test.xml", valid_xml, "text/xml")}
        )

        assert response.status_code == 200
        data = response.json()
    assert data["ok"] == True
    assert data["filename"] == "test.xml"
    assert len(data["errors"]) == 0
    assert data["summary"]["is_compliant"] == True


def test_validate_xml_invalid_nip():
    """Test validation with invalid NIP"""
    
    invalid_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<Faktura xmlns="http://crd.gov.pl/wzor/2023/06/21/12348/">
    <Naglowek>
        <KodFormularza>
            <Kod>FA</Kod>
            <WersjaSchemy>1-0E</WersjaSchemy>
        </KodFormularza>
        <WariantFormularza>1</WariantFormularza>
        <DataWystawienia>2024-01-15</DataWystawienia>
        <MiejsceWystawienia>Warszawa</MiejsceWystawienia>
        <DataSprzedazy>2024-01-15</DataSprzedazy>
        <KodWaluty>PLN</KodWaluty>
        <P_1>FV/2024/001</P_1>
        <P_2>FV/2024/001</P_2>
    </Naglowek>
    <Sprzedawca>
        <DaneIdentyfikacyjne>
            <NIP>123456789</NIP>
            <Nazwa>Test Company</Nazwa>
        </DaneIdentyfikacyjne>
        <Adres>
            <KodKraju>PL</KodKraju>
            <Miejscowosc>Warszawa</Miejscowosc>
            <KodPocztowy>00-001</KodPocztowy>
            <Poczta>Warszawa</Poczta>
        </Adres>
    </Sprzedawca>
    <Nabywca>
        <DaneIdentyfikacyjne>
            <NIP>7792439665</NIP>
            <Nazwa>Client Company</Nazwa>
        </DaneIdentyfikacyjne>
        <Adres>
            <KodKraju>PL</KodKraju>
            <Miejscowosc>Krakow</Miejscowosc>
            <KodPocztowy>30-001</KodPocztowy>
            <Poczta>Krakow</Poczta>
        </Adres>
    </Nabywca>
    <Pozycje>
        <Pozycja>
            <LpSprzedazy>1</LpSprzedazy>
            <Nazwa>Test Product</Nazwa>
            <Miara>szt.</Miara>
            <Ilosc>2</Ilosc>
            <CenaJednostkowa>100.00</CenaJednostkowa>
            <WartoscNetto>200.00</WartoscNetto>
            <StawkaPodatku>23</StawkaPodatku>
            <KwotaPodatku>46.00</KwotaPodatku>
            <WartoscBrutto>246.00</WartoscBrutto>
        </Pozycja>
    </Pozycje>
    <Podsumowanie>
        <LiczbaPozycji>1</LiczbaPozycji>
        <WartoscNetto>200.00</WartoscNetto>
        <KwotaPodatku>46.00</KwotaPodatku>
        <WartoscBrutto>246.00</WartoscBrutto>
    </Podsumowanie>
</Faktura>"""

        response = client.post(
        "/api/validate/xml",
        files={"file": ("test_invalid.xml", invalid_xml, "text/xml")}
        )

        assert response.status_code == 200
        data = response.json()
    assert data["ok"] == False
    assert data["filename"] == "test_invalid.xml"
    assert len(data["errors"]) > 0
    assert data["summary"]["is_compliant"] == False
    
    # Check that NIP error is detected
    error_messages = [e["message"] for e in data["errors"]]
    assert any("NIP" in msg or "123456789" in msg for msg in error_messages)


def test_validate_xml_malformed():
    """Test validation with malformed XML"""
    
    malformed_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<Faktura>
    <InvalidElement>
</Faktura>"""

        response = client.post(
        "/api/validate/xml",
        files={"file": ("malformed.xml", malformed_xml, "text/xml")}
        )

    # Should handle gracefully
    assert response.status_code in [200, 400]
        data = response.json()

    if response.status_code == 200:
        assert data["ok"] == False
        assert len(data["errors"]) > 0
    else:
        assert "error" in data or "detail" in data


def test_validate_xml_empty_file():
    """Test validation with empty file"""

        response = client.post(
        "/api/validate/xml",
        files={"file": ("empty.xml", b"", "text/xml")}
    )
    
    # Should handle empty file gracefully
    assert response.status_code in [200, 400]


def test_validate_endpoint_no_file():
    """Test validation endpoint without file"""
    
    response = client.post("/api/validate/xml")
    
    # Should return 422 for missing file
    assert response.status_code == 422