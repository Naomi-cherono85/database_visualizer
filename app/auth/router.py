from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .schema import Token, UserCreate
from ..models import SessionLocal
from ..utils import get_db_connection,hash_password
from .Oauth2 import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_db

# Initialize router
router = APIRouter(tags=["Authentication"])

@router.post("/auth/register", response_model=dict)
async def register_user(user: UserCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Check if user exists
        cursor.execute("SELECT username FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already registered")

        # Hash password
        hashed_password = hash_password(user.password)

        # Insert new user
        cursor.execute(
            "INSERT INTO users (username, hashed_password, email) VALUES (%s, %s, %s)",
            (user.username, hashed_password, user.email)
        )
        connection.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@router.post("/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db),):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}