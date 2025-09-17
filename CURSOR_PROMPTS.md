# 🎯 Готовые промпты для Cursor

## A. «Приведи CI к зелёному» (o3-pro, обычный режим)

```
Przejrzyj bieżący commit. Uruchom ruff/black/mypy/pytest lokalnie i wypisz pierwsze błędy.
Zapropunuj minimalny patch diffami na każdy błąd (osobne commity).
Nie zmieniaj publicznego API. Dla mypy dodawaj precyzyjne typy lub local ignore z uzasadnieniem.
```

## B. «Namespaces/XPath FA-3 + 3 кейса» (Claude Opus, Max Mode)

```
Ujednolić mapper CSV→FA-3:
- Dodaj przestrzenie nazw według FA-3.
- Zdefiniuj mapping dla 3 scenariuszy: (1) FV B2B, (2) Korekta wartości, (3) MPP.
- Dostarcz 6 golden XML (3 valid/3 invalid) + testy, które walidują przez XSD i sprawdzają obecność kluczowych pól.
- Nie łam istniejącego CLI. Jeśli zmieniasz strukturę – dopisz migrację testów.
Wypisz plan zmian i PR checklistę, potem wygeneruj diffy.
```

## C. «PDF/HTML отчёт ошибок» (o3-pro)

```
Dodaj moduł reportów: wejście = lista błędów walidacji; wyjście = HTML (i opcjonalnie PDF).
Integracja z CLI: `polcomply validate --report out/report.html`.
Test: sprawdź, że plik powstaje i zawiera liczbę błędов.
```

## D. «Excel импорт + шаблон» (Claude Opus)

```
Dodaj import Excel do FA-3:
- Wczytaj examples/invoice.xlsx jako template
- Mapuj kolumny Excel → pola FA-3 XML
- Wygeneruj XML z Excel danych
- Dodaj walidację: sprawdź wymagane pola, formaty dat, NIP
- CLI: `polcomply map excel input.xlsx --output invoice.xml`
- Test: porównaj wygenerowany XML z golden file
```

## E. «API документация + примеры» (o3-pro)

```
Uzupełnij dokumentację API:
- Dodaj OpenAPI examples dla /api/validate/xml
- Stwórz curl/wget przykłady w README
- Dodaj rate limiting info (requests/minute)
- Opisz error codes i response formaty
- Dodaj Postman collection link
```

## F. «Docker + deployment» (Claude Opus)

```
Przygotuj deployment:
- Dockerfile dla backend (FastAPI + polcomply)
- docker-compose.yml z PostgreSQL + Redis
- Nginx config dla static files
- Environment variables (.env.example)
- Health checks i logging
- Test: `docker-compose up` → API dostępne na localhost:8000
```

## G. «Тесты + покрытие» (o3-pro)

```
Dodaj comprehensive testy:
- Unit testy dla XSDValidator (edge cases)
- Integration testy dla /api/validate/xml
- Test CSV→XML mapping z różnymi formatami
- Mock KSeF API responses
- Pytest fixtures dla test data
- Coverage report: `pytest --cov=polcomply --cov-report=html`
```

## H. «Логирование + мониторинг» (Claude Opus)

```
Dodaj production-ready logging:
- Structured logging (JSON format)
- Log levels: DEBUG/INFO/WARNING/ERROR
- Request/response logging dla API
- Error tracking (Sentry integration)
- Metrics: validation requests, success rate, response time
- Log rotation i retention policy
```

## I. «Безопасность + валидация» (o3-pro)

```
Zabezpiecz API:
- Rate limiting (10 requests/minute per IP)
- File size limits (max 10MB XML)
- Input sanitization (XML injection protection)
- CORS configuration
- Security headers (HSTS, CSP)
- API key authentication для premium endpoints
```

## J. «Performance + оптимизация» (Claude Opus)

```
Zoptymalizuj performance:
- Cache XSD schema w memory
- Async file processing
- Connection pooling dla database
- Gzip compression
- Response caching (Redis)
- Load testing z locust
- Benchmark: 1000 XML files/minute
```

## 🎯 **Порядок выполнения**

### День 1 (критично):
1. **A** - Приведи CI к зелёному
2. **B** - Namespaces/XPath FA-3 + 3 кейса  
3. **C** - PDF/HTML отчёт ошибок

### День 2 (продуктовые фичи):
4. **D** - Excel импорт + шаблон
5. **E** - API документация + примеры
6. **F** - Docker + deployment

### День 3 (качество):
7. **G** - Тесты + покрытие
8. **H** - Логирование + мониторинг
9. **I** - Безопасность + валидация
10. **J** - Performance + оптимизация

## 📋 **Checklist перед каждым промптом**

- [ ] Сделал git commit текущих изменений
- [ ] Проверил что CI проходит
- [ ] Создал backup branch
- [ ] Готов к rollback если что-то сломается

## 🚀 **Быстрый старт**

1. Скопируй промпт A в Cursor
2. Выполни все diff'ы
3. Commit: `git commit -m "fix: CI green"`
4. Переходи к промпту B
5. Повторяй для всех промптов

---

*Эти промпты помогут быстро доработать проект до production-ready состояния за 3 дня*
