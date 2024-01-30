from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.user_actions import get_data
import pandas as pd

router = APIRouter()

@router.get('/get_data')
async def get_users_data(db: Session = Depends(get_db)):
    return get_data(db)