from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()


# Usar una cadena de conexión directa para evitar problemas con caracteres de escape
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_URL = (f'postgresql://postgres:{DATABASE_PASSWORD}@localhost:5432/myvoicedb')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)