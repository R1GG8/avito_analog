from pydantic import BaseModel, Field
from enums import AdStatus, OrderStatus


# Схемы для объявлений
class AdCreateDTO(BaseModel):
    seller_id: str = Field(..., example="seller_ivan_123")
    title: str = Field(..., min_length=3, example="Велосипед горный")
    description: str = Field(..., example="В отличном состоянии, пробег 1 сезон")
    price: float = Field(..., gt=0, example=15000.0)


class AdResponseDTO(BaseModel):
    id: str
    seller_id: str
    title: str
    description: str
    price: float
    status: AdStatus
    created_at: str
