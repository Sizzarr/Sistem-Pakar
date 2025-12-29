from sqlalchemy.orm import Session
from .config import settings
from .database import make_engine, make_session_local, Base

engine = make_engine(settings.DATABASE_URL)
SessionLocal = make_session_local(engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
