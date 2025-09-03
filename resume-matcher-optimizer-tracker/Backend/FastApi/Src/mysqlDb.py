from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_USER = os.environ.get("MYSQL_USER", "myuser")
DB_PASSWORD = os.environ.get("MYSQL_PASSWORD", "rootpassword")
DB_HOST = os.environ.get("MYSQL_HOST", "localhost")
DB_NAME = os.environ.get("MYSQL_DATABASE", "mydatabase")

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()