from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.user_actions import get_data
from services.auth import get_current_user
from typing import Annotated
from starlette import status

router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get('/get_data')
async def get_users_data(user: user_dependency, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    return await get_data(db)
