from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from enums import AdStatus

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from enums import AdStatus


class AdCreateDTO(BaseModel):
    seller_id: str = Field(..., example="user_123")
    title: str = Field(..., min_length=3, max_length=200, example="iPhone 13")
    description: str = Field(..., example="Отличное состояние, полный комплект")
    price: float = Field(..., gt=0, example=45000.0)
    category: str = Field(default="Другое", example="Электроника")
    image_url: Optional[str] = Field(
        default=None, example="https://example.com/phone.jpg"
    )


# Схема для частичного или полного обновления объявления (PUT / PATCH)
class AdUpdateDTO(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[AdStatus] = None


class AdResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    seller_id: str
    title: str
    description: str
    price: float
    category: str
    image_url: Optional[str]
    status: AdStatus
    created_at: str


class AdCreateDTO(BaseModel):
    seller_id: str = Field(..., example="user_123")
    title: str = Field(..., min_length=3, max_length=200, example="iPhone 13")
    description: str = Field(..., example="Отличное состояние, полный комплект")
    price: float = Field(..., gt=0, example=45000.0)
    category: str = Field(default="Другое", example="Электроника")
    image_url: Optional[str] = Field(
        default=None, example="https://example.com/phone.jpg"
    )


class AdResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    seller_id: str
    title: str
    description: str
    price: float
    category: str
    image_url: Optional[str]
    status: AdStatus
    created_at: str
