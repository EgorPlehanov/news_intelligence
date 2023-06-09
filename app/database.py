from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from app.config import settings
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




# from .models import Base

# # Удаление и создание таблиц на основе модели
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)