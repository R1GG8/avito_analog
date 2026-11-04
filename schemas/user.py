from pydantic import BaseModel, ConfigDict, EmailStr, Field


# DTO для регистрации
class UserRegisterDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="ivan_dev")
    email: EmailStr = Field(..., example="ivan@example.com")
    password: str = Field(..., min_length=6, example="secret123")


# DTO для входа
class UserLoginDTO(BaseModel):
    username: str = Field(..., example="ivan_dev")
    password: str = Field(..., example="secret123")


# DTO ответа (пароль НИКОГДА сюда не попадает!)
class UserResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    created_at: str
