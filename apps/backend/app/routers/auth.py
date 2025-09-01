from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import get_database
from app.core.security import create_access_token
from app.crud.users import authenticate_user, create_user, get_user_by_email, get_user
from app.models.user import User, UserCreate

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_database),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    if user := await get_user_by_email(db, user_id):
        return User(
            id=str(user.id),
            email=user.email,
            name=user.name,
            deriv_token=user.deriv_token,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    raise credentials_exception


async def get_current_user_from_token(token: str) -> User:
    """Get current user from JWT token (for WebSocket use)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    from app.core.database import get_database
    db = await get_database()
    
    if user := await get_user_by_email(db, user_email):
        return User(
            id=str(user.id),
            email=user.email,
            name=user.name,
            deriv_token=user.deriv_token,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    raise credentials_exception


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_database),
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(user.email)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": User(
            id=str(user.id),
            email=user.email,
            name=user.name,
            deriv_token=user.deriv_token,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
    }


@router.post("/register", response_model=User)
async def register(
    user: UserCreate,
    db = Depends(get_database),
):
    if await get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    db_user = await create_user(db, user)
    return User(
        id=str(db_user.id),
        email=db_user.email,
        name=db_user.name,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at,
    )
