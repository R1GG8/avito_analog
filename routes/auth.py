import uuid
from fastapi import APIRouter, Form, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["Auth"])

db_users: dict[str, dict] = {}  # {user_id: {"id": ..., "username": ...}}


def get_current_user(request: Request):
    """Вспомогательная функция для получения текущего пользователя из Cookie"""
    user_id = request.cookies.get("user_id")
    if user_id and user_id in db_users:
        return db_users[user_id]
    return None


@router.post("/login")
def login(response: Response, username: str = Form(...)):
    """
    Use Case 3: Вход или быстрая регистрация по имени.
    Если пользователя нет — регистрируем, если есть — авторизуем.
    """
    username = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Имя не может быть пустым")

    # Ищем пользователя или создаем нового
    user = next(
        (u for u in db_users.values() if u["username"].lower() == username.lower()),
        None,
    )
    if not user:
        user_id = f"user_{uuid.uuid4().hex[:6]}"
        user = {"id": user_id, "username": username}
        db_users[user_id] = user

    # Устанавливаем cookie с ID пользователя
    redirect = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    redirect.set_cookie(key="user_id", value=user["id"], httponly=True)
    return redirect


@router.get("/logout")
def logout():
    """Выход из аккаунта (удаление cookie)"""
    redirect = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    redirect.delete_cookie(key="user_id")
    return redirect
