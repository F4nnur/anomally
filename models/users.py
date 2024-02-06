from database import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
