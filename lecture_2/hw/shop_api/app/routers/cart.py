from typing import List, Optional
from fastapi import APIRouter, HTTPException, Response
from http import HTTPStatus
from pydantic import NonNegativeInt, PositiveInt, condecimal
from fastapi.responses import JSONResponse
from lecture_2.hw.shop_api.app.models import Cart, CartResponse, Item
from lecture_2.hw.shop_api.app.storages import carts_storage, items_storage

# from app.models import Cart, CartResponse, Item
# from app.storages import carts_storage, items_storage

router = APIRouter(prefix="/cart")

# Ограничения на положительное значение для цен
PositiveDecimal = condecimal(gt=0)  # Гарантирует, что цена будет больше нуля

@router.post("/", responses={HTTPStatus.CREATED: {"description": "Successfully created cart"}})
async def create_cart() -> JSONResponse:
    cart_id = carts_storage.create_cart()
    location = f"/cart/{cart_id}"
    return JSONResponse(
        content={"id": cart_id},
        status_code=HTTPStatus.CREATED,
        headers={"Location": location}  
    )

@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(cart_id: int) -> CartResponse:
    cart = carts_storage.get_cart(cart_id)
    if not cart:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    return CartResponse.from_cart(cart)

@router.get("/", response_model=List[CartResponse])
async def list_carts(
    offset: NonNegativeInt = 0,
    limit: PositiveInt = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_quantity: Optional[NonNegativeInt] = None,
    max_quantity: Optional[NonNegativeInt] = None
) -> List[CartResponse]:
    # Проверка на ненегативные значения для цен и количеств
    if min_price is not None and min_price < 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="min_price must be non-negative")
    
    if max_price is not None and max_price < 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="max_price must be non-negative")

    if min_quantity is not None and min_quantity < 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="min_quantity must be non-negative")

    if max_quantity is not None and max_quantity < 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="max_quantity must be non-negative")

    carts = carts_storage.paginate_filtered(
        offset, limit, min_price, max_price, min_quantity, max_quantity
    )
    return [CartResponse.from_cart(cart) for cart in carts]

@router.post("/{cart_id}/add/{item_id}", responses={HTTPStatus.OK: {"description": "Item added"}})
async def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts_storage.get_cart(cart_id)
    item = items_storage.get_item(item_id)

    if not cart:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    carts_storage.add_item_to_cart(cart_id, item)
    return Response(status_code=HTTPStatus.OK)




