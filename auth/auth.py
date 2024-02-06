from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dto.user import UserDTO
from dto.token import Token
from database import get_db

from models.users import User
from starlette import status
from typing import Annotated
from datetime import timedelta
from sqlalchemy.orm import Session
from services.auth import bcrypt_context

from services.auth import authenticate_user, create_access_token

router = APIRouter(prefix='/auth', tags=['auth'])

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
db_dependency = Annotated[Session, Depends(get_db)]


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserDTO):
    create_user_model = User(
        username=user_request.username,
        hashed_password=bcrypt_context.hash(user_request.password)
    )
    db.add(create_user_model)
    db.commit()


@router.post('/token', response_model=Token)
async def loging_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                  db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user')
    token = create_access_token(user.username, user.id, timedelta(minutes=30))
    return {'access_token': token, 'token_type': 'bearer'}
