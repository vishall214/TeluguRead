from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, TokenResponse
from app.utils.password import verify_password
from app.utils.token import create_access_token

from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest
from app.utils.password import hash_password

def login_user(data: LoginRequest, db: Session) -> TokenResponse:

    # Find user by username
    user = db.query(User).filter(
        User.username == data.username
    ).first()

    # Check username and password
    if user is None or not verify_password(
        data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Check whether account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Generate JWT access token
    access_token = create_access_token(
        user_id=user.id,
        role=user.role.value
    )

    # Return token and user details
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

def register_user(data: RegisterRequest, db: Session) -> User:

    # Check if username already exists
    existing_username = db.query(User).filter(
        User.username == data.username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create a new student account
    new_user = User(
        full_name=data.full_name,
        username=data.username,
        email=str(data.email),
        hashed_password=hash_password(data.password),
        role=UserRole.STUDENT
    )

    # Save user to PostgreSQL
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user