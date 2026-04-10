from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

# Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./the_scale.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- THE TABLES ---

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    url = Column(String, unique=True)

class Broadcast(Base):
    __tablename__ = "broadcasts"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

# This creates the tables if they don't exist
Base.metadata.create_all(bind=engine)