from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app_embalagem.config import DATABASE_URL

engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


def get_session():
    return SessionLocal()
