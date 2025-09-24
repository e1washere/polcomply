# PolComply Backend API

Professional KSeF compliance platform for Polish SMEs with comprehensive FA(3) validation and KSeF integration.

## 🚀 Features

- **FA(3) Validation**: Comprehensive invoice validation with Polish error messages and fix hints
- **KSeF Integration**: Mock KSeF API client for sandbox and production environments
- **Role-based Access Control**: Owner, Supervisor, and Accountant roles
- **Audit Logging**: Complete audit trail for all operations
- **Multi-company Support**: Manage multiple companies from single platform
- **Professional API**: RESTful API with OpenAPI documentation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PolComply Backend                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   FastAPI   │    │  PostgreSQL │    │    Redis    │ │
│  │   REST API  │    │   Database  │    │   Cache     │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ FA3Validator│    │ KSeF Client │    │  Celery     │ │
│  │   Service   │    │   (Mock)    │    │  Workers    │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Redis 6+
- Docker (optional)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd polcomply-clean/backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🔧 Configuration

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/polcomply

# Security
JWT_SECRET=your-super-secret-jwt-key
SECRET_KEY=your-super-secret-key

# Redis
REDIS_URL=redis://localhost:6379

# KSeF API
KSEF_SANDBOX_URL=https://ksef-test.mf.gov.pl
KSEF_PRODUCTION_URL=https://ksef.mf.gov.pl

# Environment
ENVIRONMENT=development
DEBUG=true
```

## 📚 API Documentation

### FA(3) Validation Endpoint

**POST** `/v1/invoices/validate-fa3`

Validates invoice data against FA(3) compliance requirements.

**Request Body:**
```json
{
  "company_id": "uuid",
  "invoice_number": "FV/2024/001",
  "issue_date": "2024-01-15",
  "sale_date": "2024-01-15",
  "due_date": "2024-02-15",
  "contractor_data": {
    "nip": "5260305408",
    "name": "Test Company Sp. z o.o.",
    "address": {
      "street": "ul. Testowa 1",
      "city": "Warszawa",
      "postal_code": "00-001",
      "country": "PL"
    }
  },
  "items": [
    {
      "name": "Test Product",
      "quantity": 2,
      "unit": "szt.",
      "net_price": 100.00,
      "vat_rate": 23
    }
  ],
  "payment_method": "transfer"
}
```

**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "invoice_data": {...}
}
```

### Error Codes

| Code | Description | Fix Hint |
|------|-------------|----------|
| FA3_001 | Missing invoice number | Enter unique invoice number |
| FA3_012 | Missing contractor NIP | Enter 10-digit contractor NIP |
| FA3_013 | Invalid NIP format | NIP must be exactly 10 digits |
| FA3_014 | Invalid NIP checksum | Check NIP checksum |
| FA3_016 | Invalid postal code | Use XX-XXX format |
| FA3_022 | Invalid VAT rate | Use allowed rates: 0%, 5%, 8%, 23% |
| FA3_023 | Net amount mismatch | Check net amount calculations |
| FA3_024 | VAT amount mismatch | Check VAT calculations |
| FA3_027 | Gross amount mismatch | Check gross = net + VAT |

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_fa3_validator.py -v

# Run with coverage
pytest --cov=app tests/
```

### Test FA3Validator directly:

```bash
python3 test_fa3_direct.py
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-based Access Control**: 
  - Owner: Full access to all companies
  - Supervisor: Manage invoices and users
  - Accountant: Create and manage invoices
- **Audit Logging**: Track all user actions with timestamps
- **Input Validation**: Comprehensive Pydantic validation
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

## 📊 Database Schema

### Core Tables

- **users**: User accounts with roles
- **companies**: Business entities
- **invoices**: FA(3) compliant invoices
- **audit_logs**: Complete audit trail
- **user_companies**: Many-to-many user-company relationships

### Key Relationships

```sql
-- Users can access multiple companies
users <-> user_companies <-> companies

-- Invoices belong to companies and users
invoices -> companies
invoices -> users (created_by)

-- Audit logs track all actions
audit_logs -> users
audit_logs -> companies
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build the image
docker build -t polcomply-backend .

# Run with docker-compose
docker-compose up -d
```

### Production Considerations

1. **Environment Variables**: Use secure secrets management
2. **Database**: Use managed PostgreSQL service
3. **Redis**: Use managed Redis service
4. **SSL/TLS**: Configure HTTPS with proper certificates
5. **Monitoring**: Set up logging and monitoring
6. **Backup**: Regular database backups
7. **Scaling**: Use load balancers and multiple instances

## 📈 Performance

- **Caching**: Redis for session and query caching
- **Database**: Optimized queries with proper indexing
- **Async Processing**: Background tasks with Celery
- **Connection Pooling**: Efficient database connections

## 🔧 Development

### Code Style

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing framework

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks
pre-commit run --all-files
```

## 📝 License

This project is licensed under the **Business Source License 1.1 (BSL)**.

**Key Terms:**
- You may use this software for development, testing, and non-production purposes without restrictions
- For production use, you may use the software for non-commercial purposes without payment
- Commercial production use requires a separate commercial license from the licensor
- On **August 30, 2029** (4 years from the license date), this license will automatically convert to the **GNU General Public License v3.0 (GPL-3.0)**

For full license terms, see the [LICENSE](../LICENSE) file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ for Polish SMEs**
