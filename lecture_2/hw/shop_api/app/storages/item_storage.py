from dataclasses import dataclass
from typing import Optional
from itertools import islice

@dataclass(slots=True)
class Item:
    id: int
    name: str
    price: float
    deleted: bool = False

class ItemStorage:
    def __init__(self):
        self.items: dict[int, Item] = {}

    def add_new_item(self, name: str, price: float) -> Item:
        new_id = max(self.items.keys(), default=0) + 1
        new_item = Item(id=new_id, name=name, price=price)
        self.items[new_id] = new_item
        return new_item

    def get_item(self, item_id: int) -> Optional[Item]:
        return self.items.get(item_id)

    def replace_item(self, item_id: int, name: str, price: float) -> Item:
        if item_id in self.items:
            self.items[item_id] = Item(id=item_id, name=name, price=price, deleted=False)
            return self.items[item_id]
        else:
            raise ValueError("Item not found")

    def update_item(self, item_id: int, name: Optional[str] = None, price: Optional[float] = None) -> Item:
        if item_id in self.items:
            if name is not None:
                self.items[item_id].name = name
            if price is not None:
                self.items[item_id].price = price
            return self.items[item_id]
        else:
            raise ValueError("Item not found")

    def delete_item(self, item_id: int) -> None:
        if item_id in self.items:
            self.items[item_id].deleted = True
        else:
            raise ValueError("Item not found")

    def paginate_items_filtered(self, offset: int = 0, limit: int = 10, min_price: Optional[float] = None, max_price: Optional[float] = None, show_deleted: bool = False) -> list[Item]:
        def filter_item(item: Item) -> bool:
            if not show_deleted and item.deleted:
                return False
            if min_price is not None and item.price < min_price:
                return False
            if max_price is not None and item.price > max_price:
                return False
            return True

        filtered_items = islice(filter(filter_item, self.items.values()), offset, offset + limit)
        return list(filtered_items)


items_storage = ItemStorage()
