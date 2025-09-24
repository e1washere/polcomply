# PolComply - FA-3 XML Validation Platform

[![CI Status](https://github.com/e1washere/polcomply/workflows/CI/badge.svg)](https://github.com/e1washere/polcomply/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](https://opensource.org/licenses/BSL-1.1)

> **Professional FA-3 XML validation for Polish e-invoicing compliance**

## 🚀 Live Demo

**Try our free XML validation service:**
- 🌐 **Web Interface**: [https://polcomply-demo.herokuapp.com](https://polcomply-demo.herokuapp.com)
- 📋 **API Documentation**: [https://polcomply-demo.herokuapp.com/docs](https://polcomply-demo.herokuapp.com/docs)
- 🔍 **Health Check**: [https://polcomply-demo.herokuapp.com/health](https://polcomply-demo.herokuapp.com/health)

## 🎯 What is PolComply?

**KSeF w 14 dni: od PDF do UPO** - Professional FA-3 XML validation platform for Polish e-invoicing compliance.

Our solution provides:
- ✅ **Instant XML validation** against official FA-3 schemas
- 📊 **Detailed error reports** with line-by-line analysis  
- 🔧 **CLI tools** for developers and automation
- 🌐 **REST API** for system integration
- 📈 **Professional reporting** with downloadable HTML reports
- 🚀 **KSeF sandbox integration** for UPO generation
- 📤 **CSV export** to Fakturownia/wFirma

## 🛠️ Quick Start

### Free Online Validation (5 weryfikacji/dzień)

1. Visit our [demo site](https://polcomply-demo.herokuapp.com)
2. Upload your XML invoice file
3. Get instant validation results
4. Download detailed compliance report

**Free limitations**: No UPO generation, no CSV export

### CLI Installation

```bash
# Install from PyPI (coming soon)
pip install polcomply

# Or install from source
git clone https://github.com/e1washere/polcomply.git
cd polcomply
pip install -e ".[dev]"
```

### Basic Usage

```bash
# Validate XML file with HTML report
polcomply validate tests/golden/fa3/valid_fv_b2b.xml --schema schemas/FA-3.xsd --report out/report.html --format table

# Map CSV to FA-3 XML
polcomply map data.csv --output invoice.xml

# Show help
polcomply --help
```

### Backend (local)

```bash
python -m venv .venv
source .venv/bin/activate

# from repository root
export PYTHONPATH=backend:.
python -m uvicorn app.main:app --reload --port 8000 --app-dir backend
# or:
# cd backend && python -m uvicorn app.main:app --reload --port 8000
```

### API Integration

```bash
# Validate XML via API
curl -F "file=@tests/golden/fa3/invalid_nip.xml" http://localhost:8000/api/validate/xml

# Send to KSeF sandbox (UPO demo)
curl -X POST "http://localhost:8000/ksef/send" \
  -H "Content-Type: application/json" \
  -d '{"xml_content": "...", "nip": "1234567890"}'
```

## 📋 Features

### Core Validation
- **FA-3 Schema Compliance**: Full validation against official Polish e-invoicing schemas
- **Real-time Processing**: Instant validation with detailed error reporting
- **Multiple Formats**: Support for various invoice types (FV, KOR, MPP)
- **Error Localization**: Precise line and column error identification

### Developer Tools
- **CLI Interface**: Command-line tools for automation and CI/CD
- **REST API**: Full REST API for system integration
- **Python SDK**: Easy integration with Python applications
- **Docker Support**: Containerized deployment options

### Professional Features
- **HTML Reports**: Beautiful, downloadable validation reports
- **Batch Processing**: Validate multiple files at once
- **CSV Mapping**: Convert CSV data to FA-3 XML format
- **Schema Auto-detection**: Automatic FA-3 schema resolution

## 🏗️ Architecture

```
polcomply/
├── cli/                 # Command-line interface
├── validators/          # XSD validation engine
├── mapping/            # CSV to FA-3 XML mapping
├── reporting/          # HTML report generation
└── tests/              # Comprehensive test suite

backend/
├── app/
│   ├── routers/        # FastAPI endpoints
│   ├── services/       # Business logic
│   └── models/         # Database models
└── static/             # Web interface
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=polcomply

# Run specific test suite
pytest tests/validators/
```

## 📊 Quality Metrics

- **Test Coverage**: 59.55% (above 50% threshold)
- **Code Quality**: Ruff + Black + MyPy compliant
- **Python Version**: 3.11+ support
- **License**: Business Source License 1.1

## 🚀 Deployment

### Docker

```bash
# Build and run
docker-compose up -d

# Access the application
open http://localhost:8000
```

### Heroku

```bash
# Deploy to Heroku
git push heroku main
```

## 📈 Commercial Plans

### 🆓 Free Tier (5 weryfikacji/dzień)
- **Online validation**: Limited XML file validation
- **Basic reports**: HTML download reports
- **No UPO**: No KSeF sandbox integration
- **No export**: No CSV export to Fakturownia/wFirma

### 💼 Professional Plans

**Starter 1299 PLN/mies**
- Do 1000 dok./mies
- UPO (sandbox/produkcyjne)
- 1 integracja (CSV Fakturownia/wFirma)
- SLA 24h

**Growth 1699 PLN/mies**
- Do 5000 dok./mies
- 3 integracje
- On-prem connector
- SLA 8h

**Onboarding 1500-2500 PLN**
- "KSeF w 14 dni" - custom implementation
- Dedicated support

[Umów demo](mailto:contact@polcomply.pl) - pokażę UPO na żywo w 60 sekund

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the Business Source License 1.1. See [LICENSE](LICENSE) for details.

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/e1washere/polcomply/wiki)
- **Issues**: [GitHub Issues](https://github.com/e1washere/polcomply/issues)
- **Email**: [contact@polcomply.pl](mailto:contact@polcomply.pl)
- **LinkedIn**: [PolComply](https://linkedin.com/company/polcomply)

## 🎯 Roadmap

- [x] **v0.1.0 (24.09.2025)**: FA-3 validator stable, CLI/API, landing
- [ ] **v0.2.0 (30.09.2025)**: KSeF sandbox UPO + CSV export + demo video
- [ ] **v0.3.0 (31.10.2025)**: 2 платящих пилота + on-prem connector
- [ ] **v0.4.0 (31.12.2025)**: 12-20 клиентов (3-8k MRR)

## 📝 Changelog

- v0.1.0: FA-3 validator stable (76 passed, 6 skipped); CLI/API; landing; Stripe links; CI on py311; main protected

---

**Built with ❤️ for the Polish e-invoicing community**

*PolComply - Making FA-3 compliance simple and reliable*
