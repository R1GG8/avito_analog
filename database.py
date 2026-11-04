from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# База данных будет храниться в файле avito.db
# Для перехода на Postgres достаточно заменить строку на:
# "postgresql://user:password@localhost:5432/avito_db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./avito.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Нужно только для SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency для внедрения сессии БД в эндпоинты FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
