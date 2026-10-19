from fastapi import FastAPI
from routes.advertisements import router as ads_router
from routes.orders import router as orders_router

app = FastAPI(
    title="Avito аналог",
    description="Демонстрация 2 Use Case: Создание объявления и Оформление заказа",
    version="1.0.0",
)

# Подключаем маршруты
app.include_router(ads_router)
app.include_router(orders_router)
