from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import OrderCreateDTO, OrderStatusUpdateDTO, OrderResponseDTO
from services import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "",
    response_model=OrderResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Оформить заказ",
)
def create_order(payload: OrderCreateDTO, db: Session = Depends(get_db)):
    try:
        return OrderService.create_order(
            db=db,
            ad_id=payload.ad_id,
            buyer_id=payload.buyer_id,
            delivery_address=payload.delivery_address,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[OrderResponseDTO], summary="Список всех заказов")
def get_all_orders(db: Session = Depends(get_db)):
    return OrderService.get_all_orders(db)


@router.get("/{order_id}", response_model=OrderResponseDTO, summary="Данные заказа")
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = OrderService.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponseDTO,
    summary="Изменить статус заказа",
)
def update_order_status(
    order_id: str, payload: OrderStatusUpdateDTO, db: Session = Depends(get_db)
):
    order = OrderService.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return OrderService.update_order_status(
        db=db, order=order, new_status=payload.status.value
    )
