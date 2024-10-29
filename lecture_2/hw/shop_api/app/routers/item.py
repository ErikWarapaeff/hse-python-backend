from fastapi import APIRouter, HTTPException, Query, Response
from http import HTTPStatus
from pydantic import NonNegativeInt, PositiveInt, condecimal
from fastapi.responses import JSONResponse
from typing import List, Optional


from lecture_2.hw.shop_api.app.models import ItemResponse, ItemRequest, ItemUpdateRequest
from lecture_2.hw.shop_api.app.storages import items_storage


# from app.models import ItemResponse, ItemRequest, ItemUpdateRequest
# from app.storages import items_storage

router = APIRouter(prefix="/item")

# Добавление ограничения на положительное значение цены
PositiveDecimal = condecimal(gt=0)  # Гарантирует, что цена будет больше нуля

@router.post("/", status_code=HTTPStatus.CREATED)
async def add_item(item: ItemRequest) -> ItemResponse:
    # Проверка на ненегативное значение цены
    if item.price <= 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Price must be greater than zero")
        
    new_item = items_storage.add_new_item(item.name, item.price)
    return ItemResponse.from_item(new_item)

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int) -> ItemResponse:
    item = items_storage.get_item(item_id)
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return ItemResponse.from_item(item)

@router.get("/", response_model=List[ItemResponse])
async def list_items(
    offset: NonNegativeInt = 0,
    limit: PositiveInt = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    show_deleted: bool = False
) -> List[ItemResponse]:
    # Проверка на ненегативные значения для фильтрации цен
    if min_price is not None and min_price < 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="min_price must be non-negative")
    
    if max_price is not None and max_price < 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="max_price must be non-negative")
    
    items = items_storage.paginate_items_filtered(offset, limit, min_price, max_price, show_deleted)
    return [ItemResponse.from_item(item) for item in items]

@router.put("/{item_id}", response_model=ItemResponse)
async def replace_item(item_id: int, item: ItemRequest) -> ItemResponse:
    # Проверка на ненегативное значение цены
    if item.price <= 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Price must be greater than zero")

    try:
        updated_item = items_storage.replace_item(item_id, item.name, item.price)
    except ValueError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return ItemResponse.from_item(updated_item)

@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item_update: ItemUpdateRequest) -> ItemResponse:
    item = items_storage.get_item(item_id)
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Item is deleted")

    if item_update.price is not None and item_update.price <= 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Price must be greater than zero")

    updated_item = items_storage.update_item(item_id, item_update.name, item_update.price)
    return ItemResponse.from_item(updated_item)

@router.delete("/{item_id}")
async def delete_item(item_id: int) -> Response:
    try:
        items_storage.delete_item(item_id)
    except ValueError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return Response(status_code=HTTPStatus.OK)