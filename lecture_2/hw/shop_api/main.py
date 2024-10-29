from lecture_2.hw.shop_api.app.routers.cart import router as cart_router
from lecture_2.hw.shop_api.app.routers.item import router as item_router
# from app.routers.cart import router as cart_router
# from app.routers.item import router as item_router
from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import start_http_server
from lecture_2.hw.shop_api.app.routers import cart, item  # Предположим, что cart.py и item.py находятся в app/routers/

# Инициализация FastAPI приложения
app = FastAPI(title="Shop API")


# Метрики Prometheus
REQUEST_COUNT = Counter('request_count', 'Количество запросов')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Время обработки запросов')

# Middleware для отслеживания метрик на уровне всего приложения
@app.middleware("http")
async def add_prometheus_metrics(request: Request, call_next):
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    return response

# Endpoint для сбора метрик
@app.get("/metrics")
async def get_metrics():
    return Response(generate_latest(), media_type="text/plain")

# Подключаем роутеры
app.include_router(cart.router)
app.include_router(item.router)