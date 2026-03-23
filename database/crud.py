from sqlalchemy.orm import Session
from .models import Broadcast

def get_broadcasts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Broadcast).order_by(Broadcast.timestamp.desc()).offset(skip).limit(limit).all()

def create_broadcast(db: Session, url: str, content: str):
    db_broadcast = Broadcast(url=url, content=content)
    db.add(db_broadcast)
    db.commit()
    db.refresh(db_broadcast)
    return db_broadcast

def get_broadcast_by_url(db: Session, url: str):
    return db.query(Broadcast).filter(Broadcast.url == url).first()
    