from fastapi import FastAPI
from database import Base, engine
import models
from routes.advertisements import router as ads_router
from routes.auth import router as auth_router
from routes.orders import router as orders_router
from routes.web import router as web_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Avito аналог",
    description="Архитектура со слоем сервисов (Service Layer)",
    version="1.0.0",
)

# 1. Веб-интерфейс (HTML)
app.include_router(web_router)

# 2. REST API (чистый JSON)
app.include_router(auth_router, prefix="/api")
app.include_router(ads_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
