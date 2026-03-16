# database.py — SQLAlchemy setup

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite use kar rahe hain (local development ke liye)
# PostgreSQL ke liye: "postgresql://user:password@localhost/dbname"
DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency — har request ke liye ek DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
