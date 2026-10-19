from datetime import datetime
import uuid
from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from enums import AdStatus, OrderStatus
from routes.orders import db_orders
from routes.advertisements import db_ads
from routes.auth import get_current_user

router = APIRouter(include_in_schema=False)  # Скрываем HTML-страницы из Swagger
templates = Jinja2Templates(directory="templates")


# ================= СТРАНИЦЫ =================


@router.get("/", response_class=HTMLResponse)
def index_page(request: Request):
    """Главная страница витрины"""
    user = get_current_user(request)
    # Исправленный вызов: request передается именованным аргументом
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "current_user": user,
            "ads": list(db_ads.values()),
            "orders": list(db_orders.values()),
        },
    )


@router.get("/login-page", response_class=HTMLResponse)
def login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse(
        request=request, name="login.html", context={"current_user": None}
    )


# ================= ДЕЙСТВИЯ ИЗ HTML-ФОРМ =================


@router.post("/web/ads/create")
def web_create_ad(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
):
    """Создание объявления через форму в браузере"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login-page", status_code=status.HTTP_303_SEE_OTHER)

    ad_id = str(uuid.uuid4())[:8]
    db_ads[ad_id] = {
        "id": ad_id,
        "seller_id": user["id"],
        "title": title,
        "description": description,
        "price": price,
        "status": AdStatus.ACTIVE,
        "created_at": datetime.now().isoformat(),
    }
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/orders/create")
def web_create_order(request: Request, ad_id: str = Form(...)):
    """Оформление заказа кнопкой 'Купить' в браузере"""
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login-page", status_code=status.HTTP_303_SEE_OTHER)

    ad = db_ads.get(ad_id)
    if not ad or ad["status"] != AdStatus.ACTIVE or ad["seller_id"] == user["id"]:
        raise HTTPException(status_code=400, detail="Ошибка оформления сделки")

    order_id = str(uuid.uuid4())[:8]
    db_orders[order_id] = {
        "id": order_id,
        "ad_id": ad["id"],
        "buyer_id": user["id"],
        "seller_id": ad["seller_id"],
        "amount": ad["price"],
        "delivery_address": "г. Москва, Пункт выдачи №1",
        "status": OrderStatus.PAID_HOLD,
        "created_at": datetime.now().isoformat(),
    }
    ad["status"] = AdStatus.RESERVED
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
