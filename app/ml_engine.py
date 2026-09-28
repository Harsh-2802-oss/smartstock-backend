"""Demand forecasting with single exponential smoothing (alpha = 0.35)."""
import math
from datetime import datetime
from typing import Iterable, List, Tuple

ALPHA = 0.35
HISTORY_DAYS = 30
HORIZON_DAYS = 7


def smooth(series: List[float], alpha: float = ALPHA) -> float:
    """Final smoothed level: L_t = alpha * x_t + (1 - alpha) * L_(t-1)."""
    if not series:
        return 0.0
    level = float(series[0])
    for x in series[1:]:
        level = alpha * x + (1 - alpha) * level
    return level


def daily_series(sales: Iterable[Tuple[int, datetime]], days: int = HISTORY_DAYS, today: datetime = None) -> List[int]:
    """Bucket (quantity, sale_time) pairs into `days` daily totals, oldest first."""
    today = (today or datetime.utcnow()).date()
    buckets = [0] * days
    for qty, when in sales:
        age = (today - when.date()).days
        if 0 <= age < days:
            buckets[days - 1 - age] += qty
    return buckets


def forecast(series: List[float], horizon: int = HORIZON_DAYS) -> List[float]:
    """SES is flat: every future day equals the last smoothed level."""
    return [round(smooth(series), 2)] * horizon


def evaluate(stock: int, series: List[float], lead_time_days: int = 3, threshold: int = 0) -> dict:
    """Forecast demand and decide whether to reorder.

    The reorder point is the larger of the product's own reorder_threshold and the
    demand expected during lead time plus a 3-day buffer, so a product with no sales
    history still follows its threshold.
    """
    level = smooth(series)
    ml_point = math.ceil(level * (lead_time_days + 3))
    point = max(threshold, ml_point)
    target = max(math.ceil(level * (HORIZON_DAYS * 2 + lead_time_days)), threshold * 2)  # ~2 weeks of cover
    status = "critical" if stock <= point else "watch" if stock <= point * 1.5 else "healthy"
    return {
        "daily_forecast": round(level, 2),
        "forecast_7d": round(level * HORIZON_DAYS, 1),
        "reorder_point": point,
        "status": status,
        "suggested_qty": max(target - stock, 1) if status == "critical" else 0,
        "days_of_cover": round(stock / level, 1) if level > 0 else None,
    }
