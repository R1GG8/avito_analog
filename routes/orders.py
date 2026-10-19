from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException, status

from enums import AdStatus, OrderStatus
from routes.advertisements import db_ads
from models import OrderCreateDTO, OrderResponseDTO

router = APIRouter(tags=["Orders"])

db_orders: dict[str, dict] = {}


@router.post(
    "/orders",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Use Case 2: Оформить заказ (Безопасная сделка)",
)
def create_order(order_data: OrderCreateDTO):
    """
    Покупатель оформляет заказ на выбранный товар.

    Бизнес-правила:
    1. Товар должен существовать.
    2. Товар должен иметь статус ACTIVE (не куплен и не зарезервирован).
    3. Нельзя купить свой собственный товар.

    Результат:
    1. Создается запись заказа со статусом PAID_HOLD.
    2. Статус объявления меняется на RESERVED.
    """
    # 1. Проверяем наличие объявления
    ad = db_ads.get(order_data.ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # 2. Проверяем доступность товара
    if ad["status"] != AdStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"Товар недоступен для покупки (текущий статус: {ad['status']})",
        )

    # 3. Проверка: продавец не может купить у самого себя
    if ad["seller_id"] == order_data.buyer_id:
        raise HTTPException(
            status_code=400, detail="Вы не можете купить свой собственный товар"
        )

    # 4. Создаем заказ
    order_id = str(uuid.uuid4())[:8]
    new_order = {
        "id": order_id,
        "ad_id": ad["id"],
        "buyer_id": order_data.buyer_id,
        "seller_id": ad["seller_id"],
        "amount": ad["price"],
        "delivery_address": order_data.delivery_address,
        "status": OrderStatus.PAID_HOLD,
        "created_at": datetime.now().isoformat(),
    }

    # 5. Применяем изменения: сохраняем заказ и резервируем товар
    db_orders[order_id] = new_order
    ad["status"] = AdStatus.RESERVED  # Меняем состояние объявления

    return new_order


@router.get(
    "/orders/{order_id}",
    response_model=OrderResponseDTO,
    summary="Получить данные заказа",
)
def get_order(order_id: str):
    order = db_orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order
