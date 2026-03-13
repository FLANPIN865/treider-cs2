"""Pydantic schemas used across service layer."""

from datetime import datetime

from pydantic import BaseModel


class CandidateSignal(BaseModel):
    item_id: int
    item_name: str
    category: str
    source_name: str
    fallback_source_used: bool
    fetched_at: datetime
    buy_price: float
    sell_price: float
    reference_price: float
    fee_amount: float
    net_profit_abs: float
    net_profit_pct: float
    liquidity_score: float
    volume_24h: float
    price_confidence: float


class RiskDecision(BaseModel):
    allowed: bool
    reasons: list[str]
    score: float
    fallback_source_used: bool
