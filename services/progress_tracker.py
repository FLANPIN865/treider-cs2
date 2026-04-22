"""Portfolio progress tracking service."""

from pydantic import BaseModel


class ProgressSnapshot(BaseModel):
    target_name: str
    target_price: float
    current_portfolio_value: float
    remaining_gap: float
    estimated_monthly_growth: float
    eta_months: float


def build_progress(
    target_name: str,
    target_price: float,
    current_portfolio_value: float,
    estimated_monthly_growth: float,
) -> ProgressSnapshot:
    gap = max(target_price - current_portfolio_value, 0.0)
    eta = gap / estimated_monthly_growth if estimated_monthly_growth > 0 else float("inf")
    return ProgressSnapshot(
        target_name=target_name,
        target_price=target_price,
        current_portfolio_value=current_portfolio_value,
        remaining_gap=round(gap, 2),
        estimated_monthly_growth=estimated_monthly_growth,
        eta_months=round(eta, 1) if eta != float("inf") else 9999,
    )
