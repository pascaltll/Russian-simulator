"""
API endpoints for user authentication.

This module handles user registration and login, issuing JWT access tokens.
"""
# Group 1: Standard libraries
# None for now.

# Group 2: Third-party libraries
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Group 3: First-party modules
from database import crud
from database.config import get_db
from schemas.user import UserCreate, Token, UserInDB
from services.auth_service import get_password_hash, create_access_token, verify_password

router = APIRouter()

@router.post(
    "/register",
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user.

    Args:
        user (UserCreate): The user data to register.
        db (Session): Database session dependency.

    Returns:
        UserInDB: The newly registered user's details.

    Raises:
        HTTPException: If the username is already registered.
    """
    db_user = crud.get_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    hashed_password = get_password_hash(user.password)
    new_user = crud.create_user(db=db, user=user, hashed_password=hashed_password)
    return new_user

@router.post("/token", response_model=Token, summary="Login and get an access token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticates a user and issues a JWT access token.

    Args:
        form_data (OAuth2PasswordRequestForm): OAuth2 form data containing username and password.
        db (Session): Database session dependency.

    Returns:
        Token: An access token and token type.

    Raises:
        HTTPException: If credentials are incorrect.
    """
    user = crud.get_by_username(db, username=form_data.username)
    if not user or not verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
