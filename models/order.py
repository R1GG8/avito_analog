from datetime import datetime
from sqlalchemy import Column, Float, ForeignKey, String
from database import Base
from enums import OrderStatus


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(50), primary_key=True, index=True)
    ad_id = Column(String(50), ForeignKey("ads.id"), nullable=False)
    buyer_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    seller_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    delivery_address = Column(String(255), nullable=False)
    status = Column(String(20), default=OrderStatus.PAID_HOLD.value, nullable=False)
    created_at = Column(String, default=lambda: datetime.now().isoformat())