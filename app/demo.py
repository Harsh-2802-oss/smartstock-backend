"""Optional: generate 30 days of sample sales so the forecaster has something to learn from."""
import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from . import ml_engine, models


def load_demo_history(db: Session, store_id: int) -> int:
    rng = random.Random(store_id * 101)
    products = db.query(models.Product).filter_by(store_id=store_id).all()
    base = {p.product_id: max(1.0, p.current_stock / rng.uniform(5, 12)) for p in products}  # units per day
    now, made = datetime.utcnow(), 0
    for d in range(ml_engine.HISTORY_DAYS, 0, -1):
        day = now - timedelta(days=d)
        lift = (1 + (ml_engine.HISTORY_DAYS - d) / 75) * (1.25 if day.weekday() >= 5 else 1)
        baskets = [dict() for _ in range(rng.randint(3, 6))]
        for p in products:
            for _ in range(max(0, round(rng.gauss(base[p.product_id] * lift, base[p.product_id] * 0.25)))):
                b = rng.choice(baskets)
                b[p.product_id] = b.get(p.product_id, 0) + 1
        for b in baskets:
            if not b:
                continue
            items = [models.SaleItem(product_id=p.product_id, quantity=b[p.product_id], unit_price=p.selling_price,
                                     unit_cost=p.cost_price) for p in products if p.product_id in b]
            db.add(models.Sale(store_id=store_id, items=items,
                               sale_time=day.replace(hour=rng.randint(9, 21), minute=rng.randint(0, 59)),
                               total_revenue=round(sum(i.quantity * i.unit_price for i in items), 2),
                               total_profit=round(sum(i.quantity * (i.unit_price - i.unit_cost) for i in items), 2)))
            made += 1
    return made
