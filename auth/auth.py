from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dto.user import UserDTO
from dto.token import Token
from database import get_db

from models.users import User
from starlette import status
from typing import Annotated
from sqlalchemy.orm import Session
from services.auth import argon2_context, create_tokens, decode_token

from services.auth import authenticate_user

router = APIRouter(prefix='/auth', tags=['auth'])

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')
db_dependency = Annotated[Session, Depends(get_db)]


@router.post('/registration', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserDTO):
    create_user_model = User(
        username=user_request.username,
        hashed_password=argon2_context.hash(user_request.password)
    )
    db.add(create_user_model)
    db.commit()
    return {"username": user_request.username}


@router.post('/login', response_model=Token)
async def loging_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                  db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user')

    access_token, refresh_token = create_tokens(user.username, user.id)
    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.post('/refresh-token', response_model=Token)
async def refresh_access_token(refresh_token: str, db: db_dependency):
    user_id = decode_token(refresh_token)['id']
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='User not found')

    access_token, _ = create_tokens(user.username, user.id)
    return {'access_token': access_token, 'refresh_token': refresh_token}

