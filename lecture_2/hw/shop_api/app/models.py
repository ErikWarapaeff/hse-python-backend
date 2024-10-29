from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional
from .storages.item_storage import Item
from .storages.cart_storage import Cart, CartItem


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    @classmethod
    def from_item(cls, item: Item) -> ItemResponse:
        """Создание ответа на основе объекта Item"""
        return cls(
            id=item.id,
            name=item.name,
            price=item.price,
            deleted=item.deleted,
        )


class ItemRequest(BaseModel):
    name: str
    price: float

    @classmethod
    def to_item(cls, item_request: ItemRequest, item_id: int) -> Item:
        """Создание объекта Item на основе запроса"""
        return Item(id=item_id, name=item_request.name, price=item_request.price)


class ItemUpdateRequest(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def update_item(cls, item: Item, update_request: ItemUpdateRequest) -> Item:
        """Обновление данных товара на основе запроса"""
        if update_request.name is not None:
            item.name = update_request.name
        if update_request.price is not None:
            item.price = update_request.price
        return item


class CartItemResponse(BaseModel):
    id: int
    name: str
    quantity: int
    is_in_stock: bool
    price: float  # Изменено на float для соответствия CartItem

    @classmethod
    def from_cart_item(cls, cart_item: CartItem) -> CartItemResponse:
        return cls(
            id=cart_item.id,
            name=cart_item.name,
            quantity=cart_item.quantity,
            is_in_stock=cart_item.is_in_stock,
            price=cart_item.price,  # Передаем цену из CartItem
        )

class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse]
    total_cost: float
    price: float

    @classmethod
    def from_cart(cls, cart: Cart) -> CartResponse:
        return cls(
            id=cart.id,
            items=[CartItemResponse.from_cart_item(item) for item in cart.items.values()],
            total_cost=cart.total_cost,
            price = cart.price  # Используем свойство total_cost
        )

    @classmethod
    def to_cart(cls, cart_response: CartResponse) -> Cart:
        """Пример обратного преобразования из CartResponse в Cart"""
        return Cart(
            id=cart_response.id,
            items={
                item.id: CartItem(
                    id=item.id,
                    name=item.name,
                    quantity=item.quantity,
                    is_in_stock=item.is_in_stock,
                    price=item.price  # Передаем цену обратно в CartItem
                ) 
                for item in cart_response.items
            },
            price=cart_response.total_cost,  # Устанавливаем цену корзины
        )
