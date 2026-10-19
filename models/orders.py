from pydantic import BaseModel, Field
from enums import AdStatus, OrderStatus


# Схемы для заказов
class OrderCreateDTO(BaseModel):
    ad_id: str = Field(..., example="id_объявления_отсюда")
    buyer_id: str = Field(..., example="buyer_olga_456")
    delivery_address: str = Field(..., example="г. Москва, ул. Ленина, д. 5, кв. 10")


class OrderResponseDTO(BaseModel):
    id: str
    ad_id: str
    buyer_id: str
    seller_id: str
    amount: float
    delivery_address: str
    status: OrderStatus
    created_at: str
