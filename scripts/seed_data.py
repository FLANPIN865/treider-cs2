"""Seed initial items and progress target."""

from db.base import Base
from db.models import Item, ProgressTarget, WatchlistItem
from db.session import SessionLocal, engine

SEED_ITEMS = [
    ("Falchion Knife | Case Hardened", "Battle-Scarred", "Knife", 210),
    ("AK-47 | Cartel", "Field-Tested", "Rifle", 18),
    ("M4A1-S | Decimator", "Field-Tested", "Rifle", 15),
    ("USP-S | Cortex", "Well-Worn", "Pistol", 8),
]


def run() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        for name, condition, category, estimated_price in SEED_ITEMS:
            existing = session.query(Item).filter(Item.name == name).first()
            if existing:
                continue
            item = Item(
                name=name,
                condition=condition,
                category=category,
                estimated_price=estimated_price,
                buy_target=estimated_price * 0.95,
                sell_target=estimated_price * 1.1,
                is_whitelisted=True,
            )
            session.add(item)
            session.flush()
            session.add(WatchlistItem(item_id=item.id, priority=1))

        if not session.query(ProgressTarget).first():
            session.add(
                ProgressTarget(
                    target_name="Butterfly Knife",
                    target_price=700,
                    estimated_monthly_growth=60,
                )
            )
        session.commit()


if __name__ == "__main__":
    run()
