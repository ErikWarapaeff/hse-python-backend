from fastapi import FastAPI

from lecture_2.hw.shop_api.app.routers.cart import router as cart_router
from lecture_2.hw.shop_api.app.routers.item import router as item_router

app = FastAPI(title="Shop API")
app.include_router(item_router)
app.include_router(cart_router)
