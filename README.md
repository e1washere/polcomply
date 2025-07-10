# PolComply - Automatyzacja e-faktur KSeF dla polskich firm

![Project Status](https://img.shields.io/badge/status-active-brightgreen)
![License](https://img.shields.io/badge/license-Proprietary-blue)
![Build](https://github.com/e1washere/polcomply/actions/workflows/ci.yml/badge.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-4.x-blue?logo=typescript)

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
