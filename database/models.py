from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Broadcast(Base):
    __tablename__ = "broadcasts"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True) # Unique to prevent double-processing
    content = Column(Text)                         # The HNN Script
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="processed")   # Helpful for tracking errors