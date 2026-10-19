from fastapi import FastAPI
from routes.advertisements import router as ads_router
from routes.auth import router as auth_router
from routes.orders import router as orders_router
from routes.web import router as web_router

app = FastAPI(
    title="Avito аналог",
    description="Демонстрация Use Cases: Авторизация, Объявления и Заказы",
    version="1.0.0",
)

# Подключение модулей
app.include_router(web_router)  # HTML-страницы интерфейса
app.include_router(auth_router)  # Авторизация (/login, /logout)
app.include_router(ads_router)  # REST API объявлений (/ads)
app.include_router(orders_router)  # REST API заказов (/orders)
