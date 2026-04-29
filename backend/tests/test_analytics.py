from app.analytics import build_loyalty_summary, list_users
from app.data_loader import load_data


def test_users_are_loaded():
    users = list_users(load_data())
    assert len(users) > 0
    assert {"id", "full_name", "financial_segment"}.issubset(users[0])


def test_summary_contains_core_blocks():
    summary = build_loyalty_summary(load_data(), 1)
    assert summary["user"]["id"] == "1"
    assert summary["totals_by_currency"]
    assert summary["forecast"]
    assert summary["offers"]
    assert summary["missions"]
    assert summary["ai_insights"]


def test_offers_match_user_segment():
    summary = build_loyalty_summary(load_data(), 1)
    segment = summary["user"]["financial_segment"]
    assert all(offer["financial_segment"] == segment for offer in summary["offers"])


def test_forecast_has_next_month_and_year():
    summary = build_loyalty_summary(load_data(), 2)
    for item in summary["forecast"].values():
        assert item["next_month"] >= 0
        assert item["next_year"] >= item["next_month"]


def test_high_segment_gets_premium_cross_sell():
    summary = build_loyalty_summary(load_data(), 4)
    products = {item["product"] for item in summary["cross_sell"]}
    assert "T-Инвестиции Premium" in products
