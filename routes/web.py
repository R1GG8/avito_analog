from typing import Optional
import urllib.parse
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models import Ad, Order
from services import AuthService, AdService, OrderService

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")

CATEGORIES = [
    "Все категории",
    "Электроника",
    "Транспорт",
    "Недвижимость",
    "Личные вещи",
    "Для дома и дачи",
    "Услуги",
    "Хобби и отдых",
]


# ================= СТРАНИЦЫ =================


@router.get("/", response_class=HTMLResponse)
def index_page(
    request: Request,
    q: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
):
    user = AuthService.get_current_user(request, db)
    ads = AdService.get_ads(
        db=db, q=q, category=category, min_price=min_price, max_price=max_price
    )
    orders = OrderService.get_all_orders(db)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "current_user": user,
            "ads": ads,
            "orders": orders,
            "categories": CATEGORIES,
            "current_q": q or "",
            "current_category": category or "Все категории",
            "current_min_price": min_price or "",
            "current_max_price": max_price or "",
        },
    )


@router.get("/ads/{ad_id}", response_class=HTMLResponse)
def ad_detail_page(ad_id: str, request: Request, db: Session = Depends(get_db)):
    user = AuthService.get_current_user(request, db)
    ad = AdService.get_ad_by_id(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    return templates.TemplateResponse(
        request=request, name="ad_detail.html", context={"current_user": user, "ad": ad}
    )


@router.get("/ads/{ad_id}/edit", response_class=HTMLResponse)
def edit_ad_page(ad_id: str, request: Request, db: Session = Depends(get_db)):
    user = AuthService.get_current_user(request, db)
    if not user:
        return RedirectResponse("/login-page", status_code=status.HTTP_303_SEE_OTHER)

    ad = AdService.get_ad_by_id(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    if ad.seller_id != user.id:
        raise HTTPException(
            status_code=403, detail="Вы можете редактировать только свои объявления"
        )

    return templates.TemplateResponse(
        request=request,
        name="edit_ad.html",
        context={"current_user": user, "ad": ad, "categories": CATEGORIES},
    )


@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request, db: Session = Depends(get_db)):
    user = AuthService.get_current_user(request, db)
    if not user:
        return RedirectResponse("/login-page", status_code=status.HTTP_303_SEE_OTHER)

    my_ads = (
        db.query(Ad)
        .filter(Ad.seller_id == user.id)
        .order_by(Ad.created_at.desc())
        .all()
    )
    my_purchases = (
        db.query(Order)
        .filter(Order.buyer_id == user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    my_sales = (
        db.query(Order)
        .filter(Order.seller_id == user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "current_user": user,
            "my_ads": my_ads,
            "my_purchases": my_purchases,
            "my_sales": my_sales,
        },
    )


@router.get("/login-page", response_class=HTMLResponse)
def login_page(request: Request, error: Optional[str] = None):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"current_user": None, "error": error},
    )


@router.get("/register-page", response_class=HTMLResponse)
def register_page(request: Request, error: Optional[str] = None):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"current_user": None, "error": error},
    )


# ================= ДЕЙСТВИЯ (ФОРМЫ) =================


@router.post("/auth/register")
def web_register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user = AuthService.register_user(
            db=db,
            username=username,
            email=email,
            password=password,
            password_confirm=password_confirm,
        )
        response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="user_id", value=user.id, httponly=True)
        return response
    except ValueError as e:
        error = urllib.parse.quote(str(e))
        return RedirectResponse(
            f"/register-page?error={error}", status_code=status.HTTP_303_SEE_OTHER
        )


@router.post("/auth/login")
def web_login(
    username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    try:
        user = AuthService.authenticate_user(
            db=db, username=username, password=password
        )
        response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="user_id", value=user.id, httponly=True)
        return response
    except ValueError as e:
        error = urllib.parse.quote(str(e))
        return RedirectResponse(
            f"/login-page?error={error}", status_code=status.HTTP_303_SEE_OTHER
        )


@router.get("/auth/logout")
@router.get("/logout")
def web_logout():
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="user_id")
    return response


@router.post("/web/ads/create")
def web_create_ad(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    image_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    user = AuthService.get_current_user(request, db)
    if not user:
        return RedirectResponse("/login-page", status_code=status.HTTP_303_SEE_OTHER)
    AdService.create_ad(
        db=db,
        seller_id=user.id,
        title=title,
        description=description,
        price=price,
        category=category,
        image_url=image_url,
    )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/ads/{ad_id}/edit")
def web_edit_ad(
    ad_id: str,
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    image_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    user = AuthService.get_current_user(request, db)
    if not user:
        return RedirectResponse("/login-page", status_code=status.HTTP_303_SEE_OTHER)
    ad = AdService.get_ad_by_id(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    try:
        AdService.update_ad(
            db=db,
            ad=ad,
            user_id=user.id,
            title=title,
            description=description,
            price=price,
            category=category,
            image_url=image_url,
        )
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RedirectResponse(f"/ads/{ad.id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/ads/{ad_id}/toggle-status")
def web_toggle_ad_status(ad_id: str, request: Request, db: Session = Depends(get_db)):
    user = AuthService.get_current_user(request, db)
    if not user:
        return RedirectResponse("/login-page", status_code=status.HTTP_303_SEE_OTHER)
    ad = AdService.get_ad_by_id(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    try:
        AdService.toggle_status(db=db, ad=ad, user_id=user.id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/ads/{ad_id}/delete")
def web_delete_ad(ad_id: str, request: Request, db: Session = Depends(get_db)):
    user = AuthService.get_current_user(request, db)
    if not user:
        return RedirectResponse("/login-page", status_code=status.HTTP_303_SEE_OTHER)
    ad = AdService.get_ad_by_id(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    try:
        AdService.delete_ad(db=db, ad=ad, user_id=user.id)
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RedirectResponse("/profile", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/orders/create")
def web_create_order(
    request: Request, ad_id: str = Form(...), db: Session = Depends(get_db)
):
    user = AuthService.get_current_user(request, db)
    if not user:
        return RedirectResponse("/login-page", status_code=status.HTTP_303_SEE_OTHER)
    try:
        OrderService.create_order(
            db=db,
            ad_id=ad_id,
            buyer_id=user.id,
            delivery_address="г. Москва, Пункт выдачи №1",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/orders/{order_id}/update-status")
def web_update_order_status(
    order_id: str,
    new_status: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db),
):
    user = AuthService.get_current_user(request, db)
    if not user:
        return RedirectResponse("/login-page", status_code=status.HTTP_303_SEE_OTHER)
    order = OrderService.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    try:
        OrderService.update_order_status(
            db=db, order=order, new_status=new_status, actor_id=user.id
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return RedirectResponse("/profile", status_code=status.HTTP_303_SEE_OTHER)
