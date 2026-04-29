from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import Any


SEGMENT_LABELS = {
    "LOW": "Стартовый",
    "MEDIUM": "Активный",
    "HIGH": "Премиальный",
}

CROSS_SELL = {
    "LOW": [
        {
            "product": "T-Мобайл",
            "reason": "снизить регулярные расходы и вернуть кэшбэк за связь",
            "cta": "Подобрать тариф",
        },
        {
            "product": "T-Инвестиции",
            "reason": "начать с учебных подборок и малых сумм",
            "cta": "Открыть брокерский счёт",
        },
        {
            "product": "Повышенные категории",
            "reason": "сконцентрировать выгоду в повседневных тратах",
            "cta": "Выбрать категории",
        },
    ],
    "MEDIUM": [
        {
            "product": "T-Инвестиции",
            "reason": "перевести свободный остаток в накопления и цели",
            "cta": "Собрать портфель",
        },
        {
            "product": "T-Мобайл Семья",
            "reason": "объединить расходы семьи и увеличить выгоду",
            "cta": "Посмотреть условия",
        },
        {
            "product": "Подписка Pro",
            "reason": "увеличить лимиты и ускорить окупаемость подписки",
            "cta": "Рассчитать выгоду",
        },
    ],
    "HIGH": [
        {
            "product": "T-Инвестиции Premium",
            "reason": "получать аналитику и персональные идеи по капиталу",
            "cta": "Запросить консультацию",
        },
        {
            "product": "All Airlines",
            "reason": "конвертировать высокие траты в travel-выгоду",
            "cta": "Усилить мили",
        },
        {
            "product": "T-Бизнес",
            "reason": "разделить личные и предпринимательские расходы",
            "cta": "Открыть счёт",
        },
    ],
}


def _month_key(value: date) -> str:
    return f"{value.year:04d}-{value.month:02d}"


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _safe_round(value: float) -> int:
    return int(round(value))


def _index_by(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {str(item[key]): item for item in items}


def list_users(data: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    return [
        {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "financial_segment": user["financial_segment"],
            "segment_label": SEGMENT_LABELS.get(user["financial_segment"], user["financial_segment"]),
        }
        for user in data["users"]
    ]


def build_loyalty_summary(data: dict[str, list[dict[str, Any]]], user_id: int) -> dict[str, Any]:
    users_by_id = _index_by(data["users"], "id")
    user = users_by_id.get(str(user_id))
    if not user:
        raise KeyError(f"User {user_id} not found")

    programs_by_id = _index_by(data["loyalty_programs"], "loyalty_program_id")
    accounts = [account for account in data["accounts"] if str(account["user_id"]) == str(user_id)]
    account_ids = {str(account["account_id"]) for account in accounts}
    account_by_id = {str(account["account_id"]): account for account in accounts}

    transactions = []
    for row in data["loyalty_history"]:
        account_id = str(row["account_id"])
        if account_id not in account_ids:
            continue

        account = account_by_id[account_id]
        program = programs_by_id[str(account["loyalty_program_id"])]
        transactions.append(
            {
                "transaction_id": row["transaction_id"],
                "account_id": account_id,
                "cashback_amount": float(row["cashback_amount"]),
                "payout_date": _parse_date(row["payout_date"]),
                "program_name": program["loyalty_program_name"],
                "currency": program["cashback_currency"],
            }
        )

    transactions.sort(key=lambda item: item["payout_date"])

    totals_by_currency: dict[str, float] = defaultdict(float)
    by_program: dict[str, float] = defaultdict(float)
    by_month: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for transaction in transactions:
        currency = transaction["currency"]
        month = _month_key(transaction["payout_date"])
        totals_by_currency[currency] += transaction["cashback_amount"]
        by_program[transaction["program_name"]] += transaction["cashback_amount"]
        by_month[month][currency] += transaction["cashback_amount"]

    monthly_chart = [
        {"month": month, **{currency: _safe_round(value) for currency, value in by_month[month].items()}}
        for month in sorted(by_month)
    ]

    forecast = _build_forecast(by_month, totals_by_currency)
    offers = _select_offers(data["offers"], user["financial_segment"])
    best_program = max(by_program.items(), key=lambda item: item[1])[0] if by_program else "программа лояльности"

    current_month_total = sum(by_month[monthly_chart[-1]["month"]].values()) if monthly_chart else 0
    missions = _build_missions(user["financial_segment"], current_month_total)

    return {
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "financial_segment": user["financial_segment"],
            "segment_label": SEGMENT_LABELS.get(user["financial_segment"], user["financial_segment"]),
        },
        "accounts": [
            {
                "account_id": account["account_id"],
                "program_name": programs_by_id[str(account["loyalty_program_id"])]["loyalty_program_name"],
                "currency": programs_by_id[str(account["loyalty_program_id"])]["cashback_currency"],
                "current_balance": round(float(account["current_balance"]), 2),
            }
            for account in accounts
        ],
        "totals_by_currency": {currency: _safe_round(value) for currency, value in totals_by_currency.items()},
        "monthly_chart": monthly_chart,
        "forecast": forecast,
        "offers": offers,
        "cross_sell": CROSS_SELL.get(user["financial_segment"], []),
        "missions": missions,
        "ai_insights": _build_ai_insights(user["financial_segment"], best_program),
        "transaction_count": len(transactions),
    }


def _build_forecast(
    by_month: dict[str, dict[str, float]],
    totals_by_currency: dict[str, float],
) -> dict[str, dict[str, int]]:
    months = sorted(by_month)[-3:]
    result: dict[str, dict[str, int]] = {}

    for currency in totals_by_currency:
        values = [by_month[month].get(currency, 0) for month in months]
        monthly_average = sum(values) / max(len(values), 1)
        result[currency] = {
            "next_month": _safe_round(monthly_average),
            "next_year": _safe_round(monthly_average * 12),
            "method": "Среднее за последние 3 активных месяца",
        }

    return result


def _select_offers(offers: list[dict[str, Any]], segment: str) -> list[dict[str, Any]]:
    return sorted(
        [offer for offer in offers if offer["financial_segment"] == segment],
        key=lambda offer: offer["cashback_percent"],
        reverse=True,
    )[:6]


def _build_missions(segment: str, current_month_total: float) -> list[dict[str, Any]]:
    target = {"LOW": 500, "MEDIUM": 1_200, "HIGH": 3_000}.get(segment, 1_000)
    remaining = max(0, target - _safe_round(current_month_total))
    progress = min(100, _safe_round(current_month_total / target * 100))

    return [
        {
            "title": "Добейте месячную цель",
            "description": f"Получите ещё {remaining} бонусов до статуса «Выгодный месяц».",
            "progress": progress,
        },
        {
            "title": "Активируйте 2 партнёрские акции",
            "description": "Офферы подобраны по финансовому сегменту и не перегружают главный экран.",
            "progress": 50,
        },
        {
            "title": "Проверьте прогноз выгоды",
            "description": "ИИ-подсказка покажет, какие продукты сильнее увеличат возврат в следующем месяце.",
            "progress": 0,
        },
    ]


def _build_ai_insights(segment: str, best_program: str) -> list[str]:
    return [
        f"Основной источник выгоды сейчас — {best_program}. Его стоит показывать первым в аналитике.",
        f"Для сегмента {segment} лучше продвигать не больше трёх cross-sell карточек на первом экране.",
        "Прогноз рассчитан по среднему за последние 3 активных месяца, поэтому он понятен пользователю и легко объясняется.",
    ]
