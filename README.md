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

PolComply is a comprehensive platform for FA-3 XML validation, helping Polish businesses ensure their electronic invoices meet government compliance requirements. Our solution provides:

- ✅ **Instant XML validation** against official FA-3 schemas
- 📊 **Detailed error reports** with line-by-line analysis
- 🔧 **CLI tools** for developers and automation
- 🌐 **REST API** for system integration
- 📈 **Professional reporting** with downloadable HTML reports

## 🛠️ Quick Start

### Free Online Validation

1. Visit our [demo site](https://polcomply-demo.herokuapp.com)
2. Upload your XML invoice file
3. Get instant validation results
4. Download detailed compliance report

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
# Validate XML file
polcomply validate invoice.xml --report report.html

# Map CSV to FA-3 XML
polcomply map data.csv --output invoice.xml

# Show help
polcomply --help
```

### API Integration

```bash
# Validate XML via API
curl -X POST "https://polcomply-demo.herokuapp.com/api/validate/xml" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@invoice.xml"
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

### 🆓 Free Tier
- **Online validation**: Unlimited XML file validation
- **Basic reports**: HTML download reports
- **Community support**: GitHub issues and documentation

### 💼 Professional Plans
- **Validator Pro**: Advanced validation features, API access
- **Integrator**: Full API integration, custom schemas
- **Pilot pod klucz**: Custom implementation, dedicated support

[Contact us](mailto:contact@polcomply.pl) for enterprise pricing and custom solutions.

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

- [ ] **Q4 2024**: Public API launch
- [ ] **Q1 2025**: Advanced reporting features
- [ ] **Q2 2025**: Multi-language support
- [ ] **Q3 2025**: Enterprise dashboard

---

**Built with ❤️ for the Polish e-invoicing community**

*PolComply - Making FA-3 compliance simple and reliable*
