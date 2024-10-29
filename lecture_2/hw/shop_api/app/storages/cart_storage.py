from dataclasses import dataclass
from typing import Optional
from itertools import islice
from lecture_2.hw.shop_api.app.storages.item_storage import Item
# from .item_storage import Item


@dataclass
class CartItem:
    id: int
    name: str
    quantity: int
    available: bool
    is_in_stock: bool  
    price: float  # Changed to float for consistency with Cart.price

@dataclass
class Cart:
    id: int
    items: dict[int, CartItem]
    price: float

    @property
    def total_cost(self) -> float:
        return sum(item.quantity * item.price for item in self.items.values())  # Calculate total cost

class CartStorage:
    def __init__(self):
        self.carts: dict[int, Cart] = {}

    def create_cart(self) -> int:
        new_id = max(self.carts.keys(), default=0) + 1
        cart = Cart(id=new_id, items={}, price=0.0)
        self.carts[new_id] = cart
        return new_id

    def get_cart(self, cart_id: int) -> Optional[Cart]:
        return self.carts.get(cart_id)

    def add_item_to_cart(self, cart_id: int, item: Item) -> CartItem:
        # Local import to avoid circular dependency
        cart = self.carts[cart_id]
        if item.id in cart.items:
            cart.items[item.id].quantity += 1
        else:
            cart.items[item.id] = CartItem(
                id=item.id,
                name=item.name,
                quantity=1,
                available=not item.deleted,
                is_in_stock=not item.deleted,  
                price=item.price  # Pass the price
            )
        cart.price += item.price
        return cart.items[item.id]

    def paginate_filtered(
        self,
        offset: int = 0,
        limit: int = 10,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_quantity: Optional[int] = None,
        max_quantity: Optional[int] = None,
    ) -> list[Cart]:
        def filter_cart(cart: Cart) -> bool:
            if min_price is not None and cart.price < min_price:
                return False
            if max_price is not None and cart.price > max_price:
                return False
            total_quantity = sum(item.quantity for item in cart.items.values())
            if min_quantity is not None and total_quantity < min_quantity:
                return False
            if max_quantity is not None and total_quantity > max_quantity:
                return False
            return True

        filtered_carts = islice(
            filter(filter_cart, self.carts.values()), offset, offset + limit
        )
        return list(filtered_carts)

carts_storage = CartStorage()

