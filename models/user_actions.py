from sqlalchemy import Integer, String, TIMESTAMP, Column
from database import Base


class UserActions(Base):
    __tablename__ = 'user_actions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    post_id = Column(Integer)
    action = Column(String)
    time = Column(TIMESTAMP)
    gender = Column(Integer)
    age = Column(Integer)
    country = Column(String)
    city = Column(String)
    os = Column(String)
    source = Column(String)
    exp_group = Column(Integer)
