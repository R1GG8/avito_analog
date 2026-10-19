from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException, status

from enums import AdStatus
from models.advertisements import AdCreateDTO, AdResponseDTO

router = APIRouter(tags=["Advertisements"])

db_ads: dict[str, dict] = {}


@router.post(
    "/ads",
    response_model=AdResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Use Case 1: Создать объявление",
)
def create_ad(ad_data: AdCreateDTO):
    """
    Продавец отправляет данные товара.
    Результат: Объявление сохраняется со статусом ACTIVE.
    """
    ad_id = str(uuid.uuid4())[:8]  # короткий читаемый ID

    new_ad = {
        "id": ad_id,
        "seller_id": ad_data.seller_id,
        "title": ad_data.title,
        "description": ad_data.description,
        "price": ad_data.price,
        "status": AdStatus.ACTIVE,
        "created_at": datetime.now().isoformat(),
    }

    # Сохраняем в память
    db_ads[ad_id] = new_ad
    return new_ad


@router.get(
    "/ads", response_model=list[AdResponseDTO], summary="Список всех объявлений"
)
def get_all_ads():
    return list(db_ads.values())


@router.get(
    "/ads/{ad_id}", response_model=AdResponseDTO, summary="Получить карточку объявления"
)
def get_ad(ad_id: str):
    ad = db_ads.get(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    return ad
