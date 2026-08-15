from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database.database import Base
class User(Base):
    __tablename__='users'
    id=Column(Integer,primary_key=True)
    name=Column(String(120),nullable=False)
    email=Column(String(255),unique=True,index=True,nullable=False)
    password_hash=Column(String(255),nullable=False)
    role=Column(String(60),default='Employee',nullable=False)
class Document(Base):
    __tablename__='documents'
    id=Column(Integer,primary_key=True)
    title=Column(String(255),nullable=False)
    filename=Column(String(255),nullable=False)
    stored_name=Column(String(255),nullable=False)
    content=Column(Text,default='')
    uploaded_by=Column(Integer,nullable=False)
    category=Column(String(120),default='General')
    created_at=Column(DateTime,default=datetime.utcnow)
