from sqlalchemy.orm import Session
from . import models

# --- Broadcast Logic ---
def get_broadcasts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Broadcast).order_by(models.Broadcast.timestamp.desc()).offset(skip).limit(limit).all()

def create_broadcast(db: Session, url: str, content: str):
    db_broadcast = models.Broadcast(url=url, content=content)
    db.add(db_broadcast)
    db.commit()
    db.refresh(db_broadcast)
    return db_broadcast

def get_broadcast_by_url(db: Session, url: str):
    return db.query(models.Broadcast).filter(models.Broadcast.url == url).first()

# --- Source Logic (The missing piece!) ---
def get_sources(db: Session):
    return db.query(models.Source).all()

def create_source(db: Session, name: str, url: str):
    db_source = models.Source(name=name, url=url)
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source