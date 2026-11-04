from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
from enums import AdStatus
from schemas import AdCreateDTO, AdUpdateDTO, AdResponseDTO
from services import AdService

router = APIRouter(prefix="/ads", tags=["Advertisements"])


@router.post(
    "",
    response_model=AdResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Создать объявление",
)
def create_ad(payload: AdCreateDTO, db: Session = Depends(get_db)):
    try:
        return AdService.create_ad(
            db=db,
            seller_id=payload.seller_id,
            title=payload.title,
            description=payload.description,
            price=payload.price,
            category=payload.category,
            image_url=payload.image_url,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "", response_model=list[AdResponseDTO], summary="Список объявлений с фильтрацией"
)
def get_all_ads(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    ad_status: Optional[AdStatus] = Query(None),
    db: Session = Depends(get_db),
):
    return AdService.get_ads(
        db=db,
        q=q,
        category=category,
        min_price=min_price,
        max_price=max_price,
        ad_status=ad_status.value if ad_status else None,
    )


@router.get(
    "/{ad_id}", response_model=AdResponseDTO, summary="Получить карточку объявления"
)
def get_ad(ad_id: str, db: Session = Depends(get_db)):
    ad = AdService.get_ad_by_id(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    return ad


@router.put(
    "/{ad_id}", response_model=AdResponseDTO, summary="Редактировать объявление"
)
def update_ad(ad_id: str, payload: AdUpdateDTO, db: Session = Depends(get_db)):
    ad = AdService.get_ad_by_id(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    try:
        return AdService.update_ad(
            db=db,
            ad=ad,
            title=payload.title,
            description=payload.description,
            price=payload.price,
            category=payload.category,
            image_url=payload.image_url,
            status=payload.status.value if payload.status else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{ad_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить объявление"
)
def delete_ad(ad_id: str, db: Session = Depends(get_db)):
    ad = AdService.get_ad_by_id(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    try:
        AdService.delete_ad(db, ad)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return None
