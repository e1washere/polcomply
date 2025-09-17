# PolComply - Automatyzacja e-faktur KSeF dla polskich firm

PolComply to kompletna platforma SaaS automatyzująca obowiązkowe e-faktury KSeF dla małych i średnich przedsiębiorstw w Polsce.

## 🎯 **БЕСПЛАТНАЯ ПРОВЕРКА XML ПО FA-3**

**Проверьте соответствие ваших фактур требованиям польского электронного документооборота FA-3 прямо сейчас!**

### ✅ Что вы получите:
- **Бесплатная валидация XML** по схеме FA-3
- **Детальная проверка** всех полей и форматов  
- **Отчет об ошибках** с указанием строк и столбцов
- **Быстрая интеграция** через REST API

### 🚀 Попробуйте прямо сейчас:
```bash
curl -X POST "https://polcomply.pl/api/validate/xml" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_invoice.xml"
```

**Или используйте наш веб-интерфейс:** [polcomply.pl](https://polcomply.pl)

## 💰 **КОММЕРЧЕСКИЕ ПЛАНЫ**

### 🎯 **Validator Pro** - 129 zł/мес
- ✅ Неограниченная проверка XML локально
- ✅ CLI инструмент для автоматизации
- ✅ Детальные отчеты об ошибках
- ✅ Поддержка всех типов FA-3 (B2B, korekta, MPP)
- ✅ Email поддержка

### 🚀 **Integrator** - 590 zł/мес  
- ✅ Все из Validator Pro
- ✅ REST API с приоритетной поддержкой
- ✅ SDK для Python/JavaScript
- ✅ Интеграция с Excel/CSV
- ✅ Автоматические отчеты в PDF/HTML
- ✅ Телефонная поддержка
- ✅ SLA 99.9%

### 🎯 **Пилот под ключ** - 3 900 zł (2 недели)
- ✅ Интеграция импорта из вашей ERP
- ✅ Настройка автоматических отчетов
- ✅ UPO-флоу мок для тестирования
- ✅ Обучение команды
- ✅ 30 дней поддержки после пилота

### 🆓 **Бесплатный пилот** (ограниченное предложение)
**Бесплатно проверим 50 ваших счетов и вышлем отчет с ошибками FA-3 в течение 24 часов**

[📝 Подать заявку на пилот](https://forms.gle/your-form-link)

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

This project is licensed under the **Business Source License 1.1 (BSL)**. 

**Key Terms:**
- You may use this software for development, testing, and non-production purposes without restrictions
- For production use, you may use the software for non-commercial purposes without payment
- Commercial production use requires a separate commercial license from the licensor
- On **August 30, 2029** (4 years from the license date), this license will automatically convert to the **GNU General Public License v3.0 (GPL-3.0)**

**What this means for you:**
- **Contributors**: You can freely contribute to the project and use it for development
- **Users**: You can use the software in production for non-commercial purposes, but commercial use requires a license
- **Businesses**: Contact the licensor for commercial licensing options

For full license terms, see the [LICENSE](LICENSE) file.

## 💬 Wsparcie

- Email: support@polcomply.pl
- Telefon: +48 22 123 45 67
- Chat: https://polcomply.pl/chat

## 🔒 Bezpieczeństwo

Znalazłeś lukę? Wyślij raport na: security@polcomply.pl

---

Stworzone z ❤️ dla polskich przedsiębiorców