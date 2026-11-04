from pydantic import BaseModel, ConfigDict, Field
from enums import OrderStatus

from pydantic import BaseModel, ConfigDict, Field
from enums import OrderStatus


class OrderCreateDTO(BaseModel):
    ad_id: str = Field(..., example="ad_id_123")
    buyer_id: str = Field(..., example="user_buyer_456")
    delivery_address: str = Field(..., example="г. Москва, ул. Ленина, д. 5")


# Схема для смены статуса заказа
class OrderStatusUpdateDTO(BaseModel):
    status: OrderStatus = Field(..., example=OrderStatus.COMPLETED)


class OrderResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ad_id: str
    buyer_id: str
    seller_id: str
    amount: float
    delivery_address: str
    status: OrderStatus
    created_at: str


# Входные данные заказа
class OrderCreateDTO(BaseModel):
    ad_id: str = Field(..., example="ad_id_123")
    buyer_id: str = Field(..., example="user_buyer_456")
    delivery_address: str = Field(..., example="г. Москва, ул. Ленина, д. 5")


# Ответ клиенту
class OrderResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ad_id: str
    buyer_id: str
    seller_id: str
    amount: float
    delivery_address: str
    status: OrderStatus
    created_at: str
