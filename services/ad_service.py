from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy.orm import Session
from models import Ad, Order, User
from enums import AdStatus


class AdService:
    @staticmethod
    def create_ad(
        db: Session,
        seller_id: str,
        title: str,
        description: str,
        price: float,
        category: str = "Другое",
        image_url: Optional[str] = None,
    ) -> Ad:
        seller = db.query(User).filter(User.id == seller_id).first()
        if not seller:
            raise ValueError("Продавец не найден в системе")

        new_ad = Ad(
            id=str(uuid.uuid4())[:8],
            seller_id=seller_id,
            title=title.strip(),
            description=description.strip(),
            price=price,
            category=category,
            image_url=image_url.strip() if image_url else None,
            status=AdStatus.ACTIVE.value,
            created_at=datetime.now().isoformat(),
        )
        db.add(new_ad)
        db.commit()
        db.refresh(new_ad)
        return new_ad

    @staticmethod
    def get_ad_by_id(db: Session, ad_id: str) -> Optional[Ad]:
        return db.query(Ad).filter(Ad.id == ad_id).first()

    @staticmethod
    def get_ads(
        db: Session,
        q: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        ad_status: Optional[str] = None,
    ) -> list[Ad]:
        query = db.query(Ad)
        if q and q.strip():
            search_term = f"%{q.strip()}%"
            query = query.filter(
                (Ad.title.ilike(search_term)) | (Ad.description.ilike(search_term))
            )
        if category and category != "Все категории":
            query = query.filter(Ad.category == category)
        if min_price is not None:
            query = query.filter(Ad.price >= min_price)
        if max_price is not None:
            query = query.filter(Ad.price <= max_price)
        if ad_status:
            query = query.filter(Ad.status == ad_status)
        return query.order_by(Ad.created_at.desc()).all()

    @staticmethod
    def update_ad(
        db: Session,
        ad: Ad,
        user_id: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        category: Optional[str] = None,
        image_url: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Ad:
        if user_id and ad.seller_id != user_id:
            raise PermissionError("Вы можете редактировать только свои объявления")
        if ad.status == AdStatus.RESERVED.value:
            raise ValueError("Нельзя изменять товар в процессе активной сделки")

        if title is not None:
            ad.title = title.strip()
        if description is not None:
            ad.description = description.strip()
        if price is not None:
            ad.price = price
        if category is not None:
            ad.category = category
        if image_url is not None:
            ad.image_url = image_url.strip() if image_url else None
        if status is not None:
            ad.status = status

        db.commit()
        db.refresh(ad)
        return ad

    @staticmethod
    def toggle_status(db: Session, ad: Ad, user_id: str) -> Ad:
        if ad.seller_id != user_id:
            raise PermissionError("Нет доступа")
        if ad.status == AdStatus.ACTIVE.value:
            ad.status = AdStatus.CLOSED.value
        elif ad.status == AdStatus.CLOSED.value:
            ad.status = AdStatus.ACTIVE.value
        db.commit()
        db.refresh(ad)
        return ad

    @staticmethod
    def delete_ad(db: Session, ad: Ad, user_id: Optional[str] = None) -> None:
        if user_id and ad.seller_id != user_id:
            raise PermissionError("Нет доступа к этому объявлению")
        if ad.status == AdStatus.RESERVED.value:
            raise ValueError("Нельзя удалить товар во время активной сделки")

        # Soft Delete: если сделки были — закрываем товар, иначе удаляем физически
        orders_count = db.query(Order).filter(Order.ad_id == ad.id).count()
        if orders_count > 0:
            ad.status = AdStatus.CLOSED.value
        else:
            db.delete(ad)
        db.commit()
