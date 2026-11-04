from datetime import datetime
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(String, default=lambda: datetime.now().isoformat())

    # Связи
    ads = relationship("Ad", back_populates="seller")
