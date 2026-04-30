# T-Bank Loyalty Hub — MVP для RadioHack

## Что сделано

Это готовый каркас двухкомпонентного решения для кейса «Единый раздел лояльности»:

1. **Web-приложение**: экран выбора тестового пользователя и раздел «Центр выгоды».
2. **Backend API**: FastAPI-сервис, который агрегирует CSV-данные, считает суммарную выгоду, прогноз, офферы, миссии и cross-sell.
3. **Документация**: продуктовая логика, гипотезы, техническое задание, тест-кейсы и CI/CD-шаблон.

## Почему такое решение соответствует кейсу

Раздел объединяет:
- кэшбэк, мили и бонусные баллы в единую аналитику;
- персональные акции партнёров с фильтрацией по финансовому сегменту;
- cross-sell продуктов экосистемы T;
- прогноз будущей выгоды;
- геймификацию через миссии;
- ИИ-подсказки с объяснимой логикой.

## Быстрый запуск

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API будет доступен на `http://localhost:8000`.

### Frontend

Откройте `frontend/index.html` в браузере.

По умолчанию фронтенд обращается к `http://localhost:8000`. Можно передать другой адрес:

```text
frontend/index.html?api=http://localhost:8000
```

Если backend не запущен, экран откроет fallback-демо на sample JSON.

## Основные эндпоинты

- `GET /health`
- `GET /api/users`
- `GET /api/users/{user_id}/loyalty-summary`
- `GET /api/offers?segment=LOW`

## Архитектура

```text
frontend/
  index.html
  styles.css
  app.js
  public/
    sample-response.json
    users.json

backend/
  app/
    main.py
    data_loader.py
    analytics.py
  tests/
    test_analytics.py

data/
  Users.csv
  Offers.csv
  LoyaltyHistory.csv
  Accounts.csv
  LoyaltyPrograms.csv

docs/
  product_brief.md
  technical_spec.md
  test_cases.md
```

## Проверка качества

```bash
cd backend
pytest
```

Покрыты 5 базовых сценариев:
1. загрузка пользователей;
2. наличие ключевых блоков раздела;
3. соответствие офферов сегменту пользователя;
4. корректность прогноза;
5. premium cross-sell для HIGH-сегмента
