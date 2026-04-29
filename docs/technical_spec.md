# Техническое задание

## Цель

Разработать MVP единого раздела лояльности для пользователей T-Банка на основе тестовых CSV-данных.

## Компоненты

### 1. Web-приложение

Функции:
- выбор тестового пользователя;
- отображение агрегированной выгоды;
- отображение прогноза;
- список партнёрских офферов;
- cross-sell карточки;
- миссии;
- ИИ-подсказки;
- светлая и тёмная тема;
- адаптивность под мобильную ширину.

### 2. Backend

Функции:
- загрузка CSV;
- агрегация выплат по валютам лояльности;
- агрегация по месяцам;
- подбор офферов по финансовому сегменту;
- расчёт прогноза;
- выдача миссий;
- выдача объяснимых ИИ-инсайтов.

## Модель данных

### Users

- id
- email
- phone_number
- full_name
- financial_segment

### Accounts

- account_id
- user_id
- loyalty_program_id
- current_balance

### LoyaltyPrograms

- loyalty_program_id
- loyalty_program_name
- cashback_currency

### LoyaltyHistory

- transaction_id
- account_id
- cashback_amount
- payout_date

### Offers

- partner_id
- partner_name
- short_description
- logo_url
- brand_color_hex
- cashback_percent
- financial_segment

## API

### GET /api/users

Возвращает список пользователей.

### GET /api/users/{user_id}/loyalty-summary

Возвращает:
- профиль пользователя;
- счета;
- total by currency;
- monthly chart;
- forecast;
- offers;
- cross_sell;
- missions;
- ai_insights.

### GET /api/offers?segment=LOW

Возвращает офферы, опционально отфильтрованные по сегменту.

## Алгоритм прогнозирования

MVP-формула:

```text
forecast_next_month(currency) = average(monthly_cashback(currency), last_3_active_months)
forecast_next_year(currency) = forecast_next_month * 12
```

Плюсы:
- понятно пользователю;
- легко объяснить в интерфейсе;
- не требует сложной ML-инфраструктуры.

Production-улучшения:
- сезонность;
- MCC/категории;
- расходы и частота покупок;
- uplift от офферов;
- персональные лимиты программ.

## Обработка ошибок

- 404 для несуществующего пользователя;
- fallback на sample JSON во фронтенде;
- healthcheck endpoint;
- CORS для локальной разработки.

## Нефункциональные требования

- responsive layout;
- dark theme;
- отсутствие падений при недоступности API;
- покрытие минимум 5 тест-кейсов;
- CI/CD через GitHub Actions.
