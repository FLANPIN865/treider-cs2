"""Repository for items."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Item, WatchlistItem


class ItemRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_watchlist_items(self) -> list[Item]:
        stmt = select(Item).join(WatchlistItem, WatchlistItem.item_id == Item.id)
        return list(self.session.scalars(stmt).all())

    def list_whitelist_items(self) -> list[Item]:
        stmt = select(Item).where(Item.is_whitelisted.is_(True), Item.is_blacklisted.is_(False))
        return list(self.session.scalars(stmt).all())

    def get_by_name(self, name: str) -> Item | None:
        stmt = select(Item).where(Item.name == name)
        return self.session.scalar(stmt)

    def add(self, item: Item) -> Item:
        self.session.add(item)
        self.session.flush()
        return item
