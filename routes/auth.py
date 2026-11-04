from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserRegisterDTO, UserLoginDTO, UserResponseDTO
from services import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация (JSON API)",
)
def api_register(
    payload: UserRegisterDTO, response: Response, db: Session = Depends(get_db)
):
    try:
        user = AuthService.register_user(
            db=db,
            username=payload.username,
            email=payload.email,
            password=payload.password,
        )
        response.set_cookie(key="user_id", value=user.id, httponly=True)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=UserResponseDTO, summary="Вход (JSON API)")
def api_login(payload: UserLoginDTO, response: Response, db: Session = Depends(get_db)):
    try:
        user = AuthService.authenticate_user(
            db=db, username=payload.username, password=payload.password
        )
        response.set_cookie(key="user_id", value=user.id, httponly=True)
        return user
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponseDTO, summary="Текущий пользователь")
def api_get_me(request: Request, db: Session = Depends(get_db)):
    user = AuthService.get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Вы не авторизованы")
    return user


@router.post("/logout", summary="Выход (JSON API)")
def api_logout(response: Response):
    response.delete_cookie(key="user_id")
    return {"message": "Успешный выход из системы"}
