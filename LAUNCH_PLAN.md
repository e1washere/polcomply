# 🚀 PolComply Launch Plan

## A) LinkedIn — тёплый запуск

### 📝 Пост для LinkedIn (PL, коротко):

```
KSeF FA-3 wchodzi w życie. Zrobiłem darmowy walidator (XML → FA-3) i raport błędów.

Szukam 5 firm do pilota (0 zł) w zamian za feedback.

✅ Бесплатная проверка XML по FA-3
✅ Детальный отчет об ошибках  
✅ API для интеграции
✅ Поддержка всех типов фактур

Formularz: https://forms.gle/your-form-link
API demo: https://polcomply.pl/api/validate/xml

#KSeF #FA3 #eFaktury #Polska #FinTech
```

### 💬 DM для бухгалтеров/SME (PL):

```
Cześć, {imię}! 

Pracuję nad PolComply — walidator FA-3 + szybki mapping z CSV/Excel.

Szukam 3–5 partnerów do krótkiego pilota (bezpłatnie, 1 tydzień).

Możemy sprawdzić 50 przykładowych faktur i odesłać raport błędów. 

Zainteresowani?

📅 Записаться: https://calendly.com/polcomply/pilot
```

### 💬 DM для интеграторов/ERP (PL):

```
Hej {imię}, 

buduję SDK/CLI do KSeF 2.0 (FA-3).

Daję endpoint do walidacji + mapping CSV→FA-3. 

Szukam partnera do integracji (Comarch/Enova/Excel).

Oddaję gotowe API + testy, my bierzemy feedback. 

Pogadamy 20 min?

📅 Записаться: https://calendly.com/polcomply/integrator
```

## B) Слот-букер

### 📅 Calendly настройки:
- **Слоты через 5 дней** после возвращения
- **2 типа встреч:**
  - Pilot Demo (30 мин) - для бухгалтеров/SME
  - Integrator Call (20 мин) - для разработчиков/ERP

### 🔗 Ссылки:
- Pilot: https://calendly.com/polcomply/pilot
- Integrator: https://calendly.com/polcomply/integrator

## C) Список ICP для первых денег

### 🎯 **Бухгалтерские фирмы** (5–50 клиентов)
**Их боль:** массовая проверка фактур клиентов
**Решение:** автоматизация валидации + отчеты
**Цена:** 129-590 zł/мес

### 🏢 **SME** (200–2000 фактур/мес)  
**Их боль:** баги в XML и штрафы от KSeF
**Решение:** валидация перед отправкой
**Цена:** 129-590 zł/мес

### 🔧 **Малые интеграторы** (под Comarch/Enova)
**Их боль:** быстро закрыть KSeF-кейсы для клиентов
**Решение:** готовое API + SDK
**Цена:** 590 zł/мес + пилоты 3 900 zł

## D) После возвращения (День 1–3) — путь к первым оплатам

### 📅 **День 1: Техническая доработка**
- [ ] Добить namespaces и XPaths под FA-3 для 3 сценариев (B2B, korekta, MPP)
- [ ] Сделать 6 «golden files» (3 валидных, 3 невалидных) + тесты
- [ ] Подключить логирование причин ошибок (коды/линии в отчёт CLI и API)

### 📅 **День 2: Продуктовые фичи**
- [ ] Автоотчёт в PDF/HTML из результатов валидации (в таблицу: id, error, line, message)
- [ ] Импорт Excel шаблона (пример examples/invoice.xlsx)
- [ ] Подготовить оффер «Pilot 7 dni» (PDF на 1 страницу) и шаблон договорённости

### 📅 **День 3: Продажи**
- [ ] 5 демо-звонков (из лидов с LinkedIn/формы)
- [ ] **Цель:** 2 платных пилота по 3 900 zł (или 1 платный + 1 barter за референс)

## 💰 **Целевые метрики**

### Неделя 1:
- 10 LinkedIn инвайтов/день
- 5 заявок на пилот
- 2 демо-звонка

### Неделя 2:
- 1 платный пилот (3 900 zł)
- 1 barter пилот (за референс)
- 2 подписчика на планы

### Месяц 1:
- 5 платных пилотов
- 10 подписчиков на планы
- 50 000 zł ARR

## 📊 **KPI для отслеживания**

- LinkedIn инвайты/день
- Заявки на пилот/день  
- Демо-звонки/день
- Конверсия в платные пилоты
- ARR (Annual Recurring Revenue)

## 🎯 **Следующие шаги**

1. **Сегодня:** Опубликовать пост в LinkedIn
2. **Завтра:** Начать отправку DM (10/день)
3. **Через 5 дней:** Начать демо-звонки
4. **Через 7 дней:** Первые платные пилоты
