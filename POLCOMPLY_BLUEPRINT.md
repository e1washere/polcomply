# PolComply - Complete Implementation Blueprint

### 1. Executive Summary

PolComply is a cloud-native SaaS platform that automates KSeF invoice compliance for Polish SMEs, eliminating manual XML generation and deadline tracking. Unlike generic accounting tools that treat Polish regulations as an afterthought, PolComply offers native KSeF API integration, real-time VAT tracking with Polish tax rules built-in, and an AI assistant that explains compliance errors in plain Polish—all designed specifically for firms racing to meet the mandatory e-invoicing deadline of April 1, 2026.

### 2. Feature List (MVP)

**Must-Have Features:**
- KSeF invoice generation and automatic submission via government API
- VAT register with automatic deadline calculations (JPK_V7M, JPK_V7K)
- Multi-company support with role-based access (owner, accountant, employee)
- Polish-language UI with all labels/forms matching official tax terminology
- Invoice templates compliant with Polish tax law (FA, korekta, zaliczka)
- Automatic retry mechanism for failed KSeF submissions
- PDF and XML export for all documents
- Audit trail for all operations (who, what, when)
- AI assistant for compliance questions in Polish

**Nice-to-Have Features:**
- Bulk invoice import from Excel/CSV
- Integration with popular Polish banks (mBank, PKO BP) for payment matching
- Mobile app for quick invoice photo capture
- Automated email reminders for VAT deadlines
- Integration with GUS REGON API for contractor verification
- White-label option for accounting firms

### 3. Target Personas & User Stories

**Primary Personas:**
1. **Małgorzata** - SME Owner (10-50 employees)
2. **Piotr** - External Accountant (manages 20+ clients)
3. **Anna** - In-house Bookkeeper (handles daily invoicing)

**Key User Stories:**
- As a SME owner, I want to generate KSeF-compliant invoices in under 60 seconds so that I can focus on running my business
- As an accountant, I want to manage multiple client companies from one dashboard so that I can efficiently serve all my clients
- As a bookkeeper, I want automatic VAT deadline reminders so that I never miss a filing deadline
- As a SME owner, I want to understand KSeF rejection reasons in plain Polish so that I can fix issues without calling my accountant
- As an accountant, I want bulk invoice upload so that I can migrate existing client data quickly
- As a bookkeeper, I want to see real-time VAT liability so that I can advise on cash flow planning

### 4. Technical Architecture Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                             PolComply Architecture                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│  │   Next.js   │     │   Next.js   │     │   Mobile    │               │
│  │   Web App   │     │  Admin Panel│     │  React Native│              │
│  │    (PWA)    │     │             │     │   (Future)  │               │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘               │
│         │                    │                    │                       │
│         └────────────────────┴────────────────────┘                      │
│                              │                                            │
│                    ┌─────────▼─────────┐                                 │
│                    │   Nginx Reverse   │                                 │
│                    │      Proxy        │                                 │
│                    └─────────┬─────────┘                                 │
│                              │                                            │
│         ┌────────────────────┴────────────────────┐                      │
│         │                                          │                      │
│  ┌──────▼──────┐                          ┌───────▼───────┐              │
│  │  FastAPI    │                          │   WebSocket   │              │
│  │   REST API  │                          │    Server     │              │
│  │  (Python)   │                          │ (Notifications)│              │
│  └──────┬──────┘                          └───────────────┘              │
│         │                                                                 │
│         ├──────────────┬───────────────┬─────────────┬─────────┐        │
│         │              │               │             │         │        │
│  ┌──────▼──────┐ ┌────▼────┐ ┌────────▼───────┐ ┌──▼───┐ ┌───▼───┐    │
│  │ PostgreSQL  │ │  Redis  │ │  Celery Worker │ │ KSeF │ │  AI   │    │
│  │     15      │ │  Cache  │ │  (Async Tasks) │ │ API  │ │Service│    │
│  │             │ │         │ │                │ │Client│ │(OpenAI)│   │
│  └─────────────┘ └─────────┘ └────────────────┘ └──────┘ └───────┘    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    External Services                              │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │    │
│  │  │  KSeF   │  │   GUS   │  │  Bank   │  │  Email  │           │    │
│  │  │   API   │  │  REGON  │  │  APIs   │  │   SMTP  │           │    │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5. Data Model

**PlantUML ERD:**
```plantuml
@startuml
entity Company {
  * id: UUID
  * nip: VARCHAR(10)
  * name: VARCHAR(255)
  * address: JSON
  * ksef_token: TEXT
  * created_at: TIMESTAMP
  * updated_at: TIMESTAMP
}

entity User {
  * id: UUID
  * email: VARCHAR(255)
  * password_hash: VARCHAR(255)
  * first_name: VARCHAR(100)
  * last_name: VARCHAR(100)
  * role: ENUM
  * is_active: BOOLEAN
  * created_at: TIMESTAMP
}

entity CompanyUser {
  * company_id: UUID
  * user_id: UUID
  * role: ENUM
  * permissions: JSON
}

entity Invoice {
  * id: UUID
  * company_id: UUID
  * invoice_number: VARCHAR(50)
  * issue_date: DATE
  * sale_date: DATE
  * contractor_data: JSON
  * items: JSON
  * net_amount: DECIMAL
  * vat_amount: DECIMAL
  * gross_amount: DECIMAL
  * ksef_reference: VARCHAR(100)
  * status: ENUM
  * created_by: UUID
  * created_at: TIMESTAMP
}

entity VatReturn {
  * id: UUID
  * company_id: UUID
  * period: VARCHAR(7)
  * type: ENUM
  * vat_due: DECIMAL
  * vat_deductible: DECIMAL
  * net_vat: DECIMAL
  * status: ENUM
  * submitted_at: TIMESTAMP
}

entity AuditLog {
  * id: UUID
  * user_id: UUID
  * company_id: UUID
  * action: VARCHAR(100)
  * entity_type: VARCHAR(50)
  * entity_id: UUID
  * changes: JSON
  * ip_address: INET
  * created_at: TIMESTAMP
}

Company ||--o{ CompanyUser
User ||--o{ CompanyUser
Company ||--o{ Invoice
Company ||--o{ VatReturn
User ||--o{ AuditLog
Company ||--o{ AuditLog
@enduml
```

**SQL DDL:**
```sql
-- Companies table
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nip VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    address JSONB NOT NULL,
    ksef_token TEXT,
    ksef_certificate TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'owner', 'accountant', 'employee')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Company-User relationship
CREATE TABLE company_users (
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('owner', 'accountant', 'employee')),
    permissions JSONB DEFAULT '{}',
    PRIMARY KEY (company_id, user_id)
);

-- Invoices table
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    invoice_number VARCHAR(50) NOT NULL,
    issue_date DATE NOT NULL,
    sale_date DATE NOT NULL,
    due_date DATE NOT NULL,
    contractor_data JSONB NOT NULL,
    items JSONB NOT NULL,
    net_amount DECIMAL(10,2) NOT NULL,
    vat_amount DECIMAL(10,2) NOT NULL,
    gross_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'PLN',
    payment_method VARCHAR(20),
    ksef_reference VARCHAR(100),
    ksef_status VARCHAR(20) DEFAULT 'pending',
    xml_content TEXT,
    pdf_url TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, invoice_number)
);

-- VAT returns table
CREATE TABLE vat_returns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    period VARCHAR(7) NOT NULL, -- YYYY-MM format
    type VARCHAR(10) NOT NULL CHECK (type IN ('JPK_V7M', 'JPK_V7K')),
    vat_due DECIMAL(10,2) DEFAULT 0,
    vat_deductible DECIMAL(10,2) DEFAULT 0,
    net_vat DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    xml_content TEXT,
    submitted_at TIMESTAMP WITH TIME ZONE,
    reference_number VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, period, type)
);

-- Audit logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    company_id UUID REFERENCES companies(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_invoices_company_date ON invoices(company_id, issue_date DESC);
CREATE INDEX idx_invoices_ksef_status ON invoices(ksef_status) WHERE ksef_status = 'pending';
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_vat_returns_period ON vat_returns(company_id, period);
```

### 6. API Specification

```yaml
openapi: 3.1.0
info:
  title: PolComply API
  version: 1.0.0
  description: API for Polish tax compliance and KSeF integration
servers:
  - url: https://api.polcomply.pl
    description: Production server
  - url: http://localhost:8000
    description: Development server

security:
  - bearerAuth: []

paths:
  /v1/auth/login:
    post:
      tags: [Authentication]
      summary: User login
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
              required: [email, password]
      responses:
        200:
          description: Login successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  refresh_token:
                    type: string
                  user:
                    $ref: '#/components/schemas/User'

  /v1/invoices:
    post:
      tags: [Invoices]
      summary: Create and send invoice to KSeF
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/InvoiceCreate'
      responses:
        201:
          description: Invoice created and queued for KSeF
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Invoice'
    
    get:
      tags: [Invoices]
      summary: List invoices with filters
      parameters:
        - name: company_id
          in: query
          schema:
            type: string
            format: uuid
        - name: from_date
          in: query
          schema:
            type: string
            format: date
        - name: to_date
          in: query
          schema:
            type: string
            format: date
        - name: status
          in: query
          schema:
            type: string
            enum: [draft, pending, sent, rejected]
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        200:
          description: List of invoices
          content:
            application/json:
              schema:
                type: object
                properties:
                  items:
                    type: array
                    items:
                      $ref: '#/components/schemas/Invoice'
                  total:
                    type: integer
                  page:
                    type: integer
                  limit:
                    type: integer

  /v1/invoices/{id}:
    get:
      tags: [Invoices]
      summary: Get invoice details
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: Invoice details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Invoice'

  /v1/vat/summary:
    get:
      tags: [VAT]
      summary: Get VAT summary for period
      parameters:
        - name: company_id
          in: query
          required: true
          schema:
            type: string
            format: uuid
        - name: period
          in: query
          required: true
          schema:
            type: string
            pattern: ^\d{4}-\d{2}$
      responses:
        200:
          description: VAT summary
          content:
            application/json:
              schema:
                type: object
                properties:
                  period:
                    type: string
                  vat_due:
                    type: number
                  vat_deductible:
                    type: number
                  net_vat:
                    type: number
                  invoice_count:
                    type: integer
                  deadline:
                    type: string
                    format: date

  /v1/ai/compliance-check:
    post:
      tags: [AI Assistant]
      summary: Check compliance and get AI recommendations
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                question:
                  type: string
                  description: Question in Polish
                context:
                  type: object
                  properties:
                    invoice_id:
                      type: string
                      format: uuid
                    error_code:
                      type: string
      responses:
        200:
          description: AI response
          content:
            application/json:
              schema:
                type: object
                properties:
                  answer:
                    type: string
                    description: Answer in Polish
                  suggestions:
                    type: array
                    items:
                      type: string
                  confidence:
                    type: number

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        first_name:
          type: string
        last_name:
          type: string
        role:
          type: string
          enum: [admin, owner, accountant, employee]

    InvoiceCreate:
      type: object
      required: [company_id, invoice_number, issue_date, sale_date, contractor_data, items]
      properties:
        company_id:
          type: string
          format: uuid
        invoice_number:
          type: string
        issue_date:
          type: string
          format: date
        sale_date:
          type: string
          format: date
        due_date:
          type: string
          format: date
        contractor_data:
          type: object
          properties:
            nip:
              type: string
            name:
              type: string
            address:
              type: object
        items:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
              quantity:
                type: number
              unit:
                type: string
              net_price:
                type: number
              vat_rate:
                type: integer
              net_amount:
                type: number
              vat_amount:
                type: number

    Invoice:
      allOf:
        - $ref: '#/components/schemas/InvoiceCreate'
        - type: object
          properties:
            id:
              type: string
              format: uuid
            net_amount:
              type: number
            vat_amount:
              type: number
            gross_amount:
              type: number
            ksef_reference:
              type: string
            ksef_status:
              type: string
              enum: [pending, sent, rejected]
            created_at:
              type: string
              format: date-time
            created_by:
              type: string
              format: uuid
```

### 7. Backend Code Skeleton

**File Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── user.py
│   │   ├── invoice.py
│   │   └── audit.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── invoice.py
│   │   └── vat.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── invoices.py
│   │   ├── vat.py
│   │   └── ai.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ksef_client.py
│   │   ├── invoice_service.py
│   │   ├── vat_calculator.py
│   │   └── ai_assistant.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── validators.py
│   │   └── xml_builder.py
│   └── workers/
│       ├── __init__.py
│       └── tasks.py
├── alembic/
│   └── versions/
├── tests/
├── requirements.txt
├── Dockerfile
└── .env.example
```

### 8. Frontend Code Skeleton

**File Structure:**
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── invoices/
│   │   │   ├── page.tsx
│   │   │   ├── new/
│   │   │   │   └── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── vat/
│   │   │   └── page.tsx
│   │   └── settings/
│   │       └── page.tsx
├── components/
│   ├── ui/
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── form.tsx
│   │   └── toast.tsx
│   ├── invoice/
│   │   ├── InvoiceForm.tsx
│   │   ├── InvoiceList.tsx
│   │   └── InvoicePreview.tsx
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── lib/
│   ├── api.ts
│   ├── auth.ts
│   ├── utils.ts
│   └── hooks/
│       ├── useAuth.ts
│       └── useInvoices.ts
├── public/
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
└── Dockerfile
```

### 9. Dev & Prod Infrastructure

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: polcomply
      POSTGRES_USER: polcomply
      POSTGRES_PASSWORD: ${DB_PASSWORD:-secretpass}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U polcomply"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://polcomply:${DB_PASSWORD:-secretpass}@postgres:5432/polcomply
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET: ${JWT_SECRET:-your-secret-key}
      KSEF_API_URL: ${KSEF_API_URL:-https://ksef-test.mf.gov.pl}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery:
    build: ./backend
    command: celery -A app.workers.tasks worker --loglevel=info
    volumes:
      - ./backend:/app
    environment:
      DATABASE_URL: postgresql://polcomply:${DB_PASSWORD:-secretpass}@postgres:5432/polcomply
      REDIS_URL: redis://redis:6379/0
      KSEF_API_URL: ${KSEF_API_URL:-https://ksef-test.mf.gov.pl}
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/v1
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
```

**Makefile:**
```makefile
.PHONY: help dev stop clean test build deploy

help:
	@echo "Available commands:"
	@echo "  make dev    - Start development environment"
	@echo "  make stop   - Stop all containers"
	@echo "  make clean  - Clean up containers and volumes"
	@echo "  make test   - Run tests"
	@echo "  make build  - Build production images"
	@echo "  make deploy - Deploy to production"

dev:
	@echo "Starting development environment..."
	@cp .env.example .env 2>/dev/null || true
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Running database migrations..."
	docker-compose exec backend alembic upgrade head
	@echo "\n✅ Development environment is ready!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000/docs"
	@echo "Database: localhost:5432"

stop:
	docker-compose down

clean:
	docker-compose down -v
	rm -rf backend/__pycache__
	rm -rf frontend/.next
	rm -rf frontend/node_modules

test:
	docker-compose exec backend pytest
	docker-compose exec frontend npm test

build:
	docker build -t polcomply-backend:latest ./backend
	docker build -t polcomply-frontend:latest ./frontend

deploy:
	@echo "Deploying to production..."
	./scripts/deploy.sh
```

### 10. Security & Compliance Notes

**Security Implementation Checklist:**
- ✅ JWT-based authentication with refresh tokens (RS256 algorithm)
- ✅ Role-based access control (RBAC) with company-level isolation
- ✅ HTTPS enforcement via nginx with Let's Encrypt certificates
- ✅ Database encryption at rest using PostgreSQL TDE
- ✅ Sensitive data encryption (KSeF tokens, certificates) using AES-256
- ✅ API rate limiting: 100 requests/minute per user
- ✅ Input validation on all endpoints using Pydantic
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ XSS prevention with React's automatic escaping
- ✅ CSRF protection using double-submit cookies
- ✅ Audit logging for all data modifications
- ✅ Password policy: min 12 chars, complexity requirements
- ✅ 2FA support via TOTP (Google Authenticator)

**GDPR Compliance:**
- ✅ Privacy policy and cookie consent banner
- ✅ Data export functionality (JSON/CSV)
- ✅ Right to deletion (soft delete with 30-day retention)
- ✅ Data processing agreements template
- ✅ Encryption of personal data in transit and at rest
- ✅ Access logs retention: 90 days
- ✅ Regular security audits scheduled quarterly

### 11. AI Assistant Design

**Polish Language Prompt Template:**
```python
SYSTEM_PROMPT = """Jesteś ekspertem podatkowym PolComply AI, specjalizującym się w polskich przepisach dotyczących 
e-fakturowania (KSeF) i VAT. Odpowiadasz TYLKO po polsku, używając prostego języka zrozumiałego dla właścicieli 
małych firm. Zawsze podajesz konkretne kroki do rozwiązania problemu.

Kontekst:
- Firma: {company_name} (NIP: {nip})
- Problem: {error_type}
- Szczegóły: {error_details}
"""

USER_PROMPT_TEMPLATE = """
Pytanie: {question}

Dodatkowe informacje:
- Numer faktury: {invoice_number}
- Data wystawienia: {issue_date}
- Kod błędu KSeF: {ksef_error_code}
- Komunikat błędu: {error_message}

Proszę wyjaśnić:
1. Co oznacza ten błąd?
2. Jak go naprawić krok po kroku?
3. Jak uniknąć tego w przyszłości?
"""

# Example implementation
async def process_compliance_question(
    question: str,
    invoice_id: Optional[UUID],
    error_code: Optional[str]
) -> AIResponse:
    # Fetch context
    invoice = await get_invoice(invoice_id) if invoice_id else None
    error_details = KSEF_ERROR_MAPPINGS.get(error_code, {})
    
    # Build prompts
    system_prompt = SYSTEM_PROMPT.format(
        company_name=invoice.company.name if invoice else "Twoja firma",
        nip=invoice.company.nip if invoice else "N/A",
        error_type=error_details.get("type", "Ogólny"),
        error_details=error_details.get("description", "")
    )
    
    user_prompt = USER_PROMPT_TEMPLATE.format(
        question=question,
        invoice_number=invoice.invoice_number if invoice else "N/A",
        issue_date=invoice.issue_date if invoice else "N/A",
        ksef_error_code=error_code or "N/A",
        error_message=error_details.get("message", "")
    )
    
    # Call LLM
    response = await openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return AIResponse(
        answer=response.choices[0].message.content,
        confidence=0.95 if error_code in KSEF_ERROR_MAPPINGS else 0.7,
        suggestions=extract_action_items(response.choices[0].message.content)
    )
```

### 12. KSeF Integration Details

**Authentication Workflow:**
```python
# 1. Initial authentication with qualified certificate
async def authenticate_ksef(company: Company) -> KSeFSession:
    # Load certificate
    cert = load_certificate(company.ksef_certificate)
    
    # Generate challenge
    challenge_response = await ksef_client.post(
        "/api/session/AuthorisationChallenge",
        json={
            "contextIdentifier": {
                "type": "onip",
                "identifier": company.nip
            }
        }
    )
    
    # Sign challenge with certificate
    signed_challenge = sign_with_certificate(
        challenge_response["challenge"],
        cert.private_key
    )
    
    # Initialize session
    session_response = await ksef_client.post(
        "/api/session/InitSigned",
        json={
            "challenge": challenge_response["challenge"],
            "signature": signed_challenge
        }
    )
    
    return KSeFSession(
        token=session_response["sessionToken"],
        reference_number=session_response["referenceNumber"],
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )

# 2. Invoice submission with retry logic
async def submit_invoice_to_ksef(
    invoice: Invoice,
    session: KSeFSession,
    max_retries: int = 3
) -> KSeFResponse:
    xml_content = build_invoice_xml(invoice)
    
    for attempt in range(max_retries):
        try:
            response = await ksef_client.post(
                "/api/invoice/send",
                headers={"SessionToken": session.token},
                data=xml_content,
                content_type="application/xml"
            )
            
            # Update invoice with KSeF reference
            invoice.ksef_reference = response["referenceNumber"]
            invoice.ksef_status = "sent"
            await invoice.save()
            
            return response
            
        except KSeFRateLimitError:
            # Exponential backoff
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)
            
        except KSeFValidationError as e:
            # Log validation error for AI assistant
            await log_ksef_error(invoice, e.code, e.message)
            raise
    
    raise KSeFMaxRetriesError()
```

**XML Schema Reference:**
- FA Schema: https://www.gov.pl/web/kas/struktury-dokumentow-xml#FA
- Authentication: https://ksef.mf.gov.pl/api/schema/gtw/svc/types/2021/10/01/0001

**Rate Limits:**
- Test environment: 20 requests/minute
- Production: 100 requests/minute per NIP
- Batch submissions: max 100 invoices per request

### 13. Roadmap & Milestones

**90-Day Implementation Plan:**

**Week 1-2: Foundation**
- Set up development environment and CI/CD pipeline
- Implement authentication and user management
- Create database schema and migrations
- Team: 1 Backend Dev, 1 DevOps

**Week 3-4: Core Invoice Module**
- Build invoice creation and management API
- Implement Polish VAT calculation rules
- Create invoice form UI with validation
- Team: 1 Backend Dev, 1 Frontend Dev

**Week 5-6: KSeF Integration**
- Implement KSeF authentication flow
- Build XML generation for invoices
- Add submission queue with Celery
- Team: 1 Backend Dev, 1 Integration Specialist

**Week 7-8: VAT Module & Reporting**
- Implement VAT register and calculations
- Build JPK_V7M/K generation
- Create dashboard with key metrics
- Team: 1 Backend Dev, 1 Frontend Dev

**Week 9-10: AI Assistant**
- Integrate OpenAI API
- Train on Polish tax regulations
- Build chat interface
- Team: 1 ML Engineer, 1 Frontend Dev

**Week 11-12: Testing & Polish Localization**
- End-to-end testing with accountants
- Polish UI/UX review and refinement
- Performance optimization
- Security audit
- Team: Full team + 2 QA Engineers

**Week 13: Launch Preparation**
- Production deployment
- Documentation and training materials
- Marketing website
- Team: Full team + Marketing

**Success Metrics:**
- 50 beta users by end of Week 12
- <2s invoice generation time
- 99% KSeF submission success rate
- 4.5+ user satisfaction score
- Zero security incidents

### 14. Go-to-Market & Pricing

**Pricing Tiers:**

1. **Starter (Darmowy)**
   - Do 5 faktur/miesiąc
   - 1 firma
   - Podstawowa integracja KSeF
   - Email support

2. **Professional (99 PLN/miesiąc)**
   - Do 100 faktur/miesiąc
   - 1 firma
   - Pełna integracja KSeF
   - Asystent AI
   - Automatyczne JPK
   - Chat support

3. **Business (299 PLN/miesiąc)**
   - Nieograniczone faktury
   - Do 5 firm
   - API access
   - Priorytetowe wsparcie
   - Szkolenie online

4. **Enterprise (Cena indywidualna)**
   - Nieograniczone firmy
   - White-label
   - Dedykowany opiekun
   - SLA 99.9%
   - Integracje na zamówienie

**Go-to-Market Strategy:**

1. **Accountant Referral Program**
   - 20% prowizji przez 12 miesięcy
   - Darmowe konto dla biura rachunkowego
   - Co-branded marketing materials

2. **Content Marketing**
   - Blog: "KSeF krok po kroku"
   - YouTube: Tutoriale w języku polskim
   - Webinary z ekspertami podatkowymi

3. **Partnerships**
   - Integracja z Allegro, Shoper, WooCommerce
   - Współpraca z izbami gospodarczymi
   - Certification program dla księgowych

4. **Launch Sequence**
   - Month 1: Closed beta (100 users)
   - Month 2: Open beta with Starter plan
   - Month 3: Full launch with paid plans
   - Month 4: Enterprise sales push

### 15. README.md

```markdown
# PolComply - Automatyzacja e-faktur KSeF dla polskich firm

PolComply to kompletna platforma SaaS automatyzująca obowiązkowe e-faktury KSeF dla małych i średnich przedsiębiorstw w Polsce.

## 🚀 Szybki start

### Wymagania
- Docker Desktop 4.0+
- 8GB RAM minimum
- 10GB wolnego miejsca

### Instalacja i uruchomienie

1. Sklonuj repozytorium:
```bash
git clone https://github.com/polcomply/polcomply.git
cd polcomply
```

2. Uruchom środowisko deweloperskie:
```bash
make dev
```

3. Aplikacja będzie dostępna pod adresami:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs
   - pgAdmin: http://localhost:5050

### Domyślne dane logowania
- Email: demo@polcomply.pl
- Hasło: Demo123!@#

## 📋 Funkcjonalności

- ✅ Generowanie faktur zgodnych z KSeF
- ✅ Automatyczne wysyłanie do systemu KSeF
- ✅ Śledzenie statusów i obsługa błędów
- ✅ Rejestr VAT z automatycznymi terminami
- ✅ Asystent AI wyjaśniający przepisy po polsku
- ✅ Wielofirmowość z kontrolą dostępu
- ✅ Eksport do PDF i XML

## 🏗️ Architektura

```
Frontend (Next.js + TypeScript) → Backend (FastAPI + Python) → PostgreSQL
                                                            → Redis (cache)
                                                            → Celery (async)
                                                            → KSeF API
```

## 🔧 Konfiguracja

Skopiuj `.env.example` do `.env` i uzupełnij:

```env
# Wymagane
DATABASE_URL=postgresql://polcomply:password@localhost:5432/polcomply
JWT_SECRET=your-secret-key-min-32-chars
KSEF_API_URL=https://ksef-test.mf.gov.pl

# Opcjonalne
OPENAI_API_KEY=sk-...  # Dla asystenta AI
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 🧪 Testy

```bash
# Backend testy
make test-backend

# Frontend testy
make test-frontend

# E2E testy
make test-e2e
```

## 📦 Deployment

### Produkcja (Docker Swarm)
```bash
make build
make deploy
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

## 📚 Dokumentacja

- [Dokumentacja API](http://localhost:8000/docs)
- [Podręcznik użytkownika](docs/user-guide-pl.md)
- [Integracja KSeF](docs/ksef-integration.md)

## 🤝 Współpraca

1. Fork repozytorium
2. Stwórz branch (`git checkout -b feature/AmazingFeature`)
3. Commit zmiany (`git commit -m 'Add AmazingFeature'`)
4. Push do brancha (`git push origin feature/AmazingFeature`)
5. Otwórz Pull Request

## 📄 Licencja

Proprietary - All rights reserved © 2024 PolComply

## 💬 Wsparcie

- Email: support@polcomply.pl
- Telefon: +48 22 123 45 67
- Chat: https://polcomply.pl/chat

## 🔒 Bezpieczeństwo

Znalazłeś lukę? Wyślij raport na: security@polcomply.pl

---

Stworzone z ❤️ dla polskich przedsiębiorców