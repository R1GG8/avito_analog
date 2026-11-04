from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy.orm import Session
from models import Ad, Order, User
from enums import AdStatus, OrderStatus


class OrderService:
    @staticmethod
    def create_order(
        db: Session, ad_id: str, buyer_id: str, delivery_address: str
    ) -> Order:
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            raise ValueError("Товар не найден")
        if ad.status != AdStatus.ACTIVE.value:
            raise ValueError(f"Товар недоступен для покупки (статус: {ad.status})")
        if ad.seller_id == buyer_id:
            raise ValueError("Вы не можете купить свой собственный товар")

        buyer = db.query(User).filter(User.id == buyer_id).first()
        if not buyer:
            raise ValueError("Покупатель не найден")

        order_id = str(uuid.uuid4())[:8]
        new_order = Order(
            id=order_id,
            ad_id=ad.id,
            buyer_id=buyer_id,
            seller_id=ad.seller_id,
            amount=ad.price,
            delivery_address=delivery_address,
            status=OrderStatus.PAID_HOLD.value,
            created_at=datetime.now().isoformat(),
        )
        ad.status = AdStatus.RESERVED.value
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order

    @staticmethod
    def get_order_by_id(db: Session, order_id: str) -> Optional[Order]:
        return db.query(Order).filter(Order.id == order_id).first()

    @staticmethod
    def get_all_orders(db: Session) -> list[Order]:
        return db.query(Order).order_by(Order.created_at.desc()).all()

    @staticmethod
    def update_order_status(
        db: Session, order: Order, new_status: str, actor_id: Optional[str] = None
    ) -> Order:
        ad = db.query(Ad).filter(Ad.id == order.ad_id).first()

        if new_status == OrderStatus.COMPLETED.value:
            if actor_id and order.buyer_id != actor_id:
                raise PermissionError("Только покупатель может подтвердить получение")
            order.status = OrderStatus.COMPLETED.value
            if ad:
                ad.status = AdStatus.CLOSED.value

        elif new_status == "SHIPPED":
            if actor_id and order.seller_id != actor_id:
                raise PermissionError("Только продавец может отметить отправку")
            order.status = "SHIPPED"

        elif new_status == OrderStatus.CANCELLED.value:
            if actor_id and actor_id not in [order.buyer_id, order.seller_id]:
                raise PermissionError("Нет прав для отмены заказа")
            order.status = OrderStatus.CANCELLED.value
            if ad:
                ad.status = AdStatus.ACTIVE.value  # Возврат в каталог

        else:
            order.status = new_status

        db.commit()
        db.refresh(order)
        return order
