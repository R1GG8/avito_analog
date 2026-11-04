from datetime import datetime
from sqlalchemy import Column, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from database import Base
from enums import AdStatus


class Ad(Base):
    __tablename__ = "ads"

    id = Column(String(50), primary_key=True, index=True)
    seller_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String(50), default="Другое", nullable=False)  # <-- НОВОЕ ПОЛЕ
    image_url = Column(String(500), nullable=True)  # <-- НОВОЕ ПОЛЕ (ссылка на фото)
    status = Column(String(20), default=AdStatus.ACTIVE.value, nullable=False)
    created_at = Column(String, default=lambda: datetime.now().isoformat())

    # Связи
    seller = relationship("User", back_populates="ads")
