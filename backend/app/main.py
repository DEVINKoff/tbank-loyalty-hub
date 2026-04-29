from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .analytics import build_loyalty_summary, list_users
from .data_loader import load_data


app = FastAPI(
    title="T-Bank Loyalty Hub API",
    version="1.0.0",
    description="Backend MVP for the RadioHack loyalty case.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/users")
def get_users() -> list[dict]:
    return list_users(load_data())


@app.get("/api/users/{user_id}/loyalty-summary")
def get_loyalty_summary(user_id: int) -> dict:
    try:
        return build_loyalty_summary(load_data(), user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/offers")
def get_offers(segment: str | None = None) -> list[dict]:
    data = load_data()
    offers = data["offers"]
    if segment:
        offers = [offer for offer in offers if offer["financial_segment"] == segment.upper()]
    return sorted(offers, key=lambda offer: offer["cashback_percent"], reverse=True)
