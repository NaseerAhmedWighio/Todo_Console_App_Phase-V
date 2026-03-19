import os
import uuid as uuid_lib
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from ..database.session import get_session
from ..models.email_verification import EmailVerification
from ..models.user import (
    User,
    UserCreate,
    UserLogin,
    UserResponse,
    get_utc_now,
    hash_password,
    is_google_email,
    validate_email_format,
    verify_password,
)
from ..services.email_service import email_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


@router.post("/register")
def register(user_create: UserCreate, session: Session = Depends(get_session)):
    """Register a new user"""
    try:
        # Validate email format
        if not validate_email_format(user_create.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")

        # Check if Google email validation is required
        if user_create.google_email_only:
            if not is_google_email(user_create.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration requires a Google email address (gmail.com or googlemail.com)",
                )
        else:
            # Even if not required, check if it's a Google email for logging/analytics
            is_google = is_google_email(user_create.email)
            print(f"User registration - Google email: {is_google}, Email: {user_create.email}")

        # Check if user already exists
        existing_user = session.exec(select(User).where(User.email == user_create.email)).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

        # Hash the password
        hashed_password = hash_password(user_create.password)

        # Create the user (verified by default)
        db_user = User(
            email=user_create.email,
            name=user_create.name,
            password_hash=hashed_password,
            is_email_verified=True,
            email_verified_at=get_utc_now(),
        )

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        # Create access token for the new user
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user.id), "email": db_user.email, "verified": True}, expires_delta=access_token_expires
        )

        return {
            "success": True,
            "message": "Registration successful",
            "data": {
                "user": UserResponse.model_validate(db_user),
                "token": access_token,
                "is_google_email": is_google_email(user_create.email),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        # Log the error for debugging
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Registration failed: {str(e)}")


@router.post("/login")
def login(user_login: UserLogin, session: Session = Depends(get_session)):
    """Login a user and return access token"""
    # Find user by email
    print(f"Login attempt for email: {user_login.email}")
    user = session.exec(select(User).where(User.email == user_login.email)).first()

    if not user:
        print(f"User not found: {user_login.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    password_valid = verify_password(user_login.password, user.password_hash)
    print(f"Password validation result: {password_valid}")

    if not password_valid:
        print(f"Invalid password for user: {user_login.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "verified": True}, expires_delta=access_token_expires
    )

    return {"success": True, "data": {"user": UserResponse.model_validate(user), "token": access_token}}


@router.get("/me", response_model=UserResponse)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)
):
    """Get current user info using JWT token"""
    try:
        import uuid

        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Convert string to UUID
        user_id = uuid.UUID(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserResponse.model_validate(user)


@router.post("/logout")
def logout():
    """Logout endpoint (frontend handles token removal)"""
    return {"message": "Logged out successfully"}


@router.post("/verify-email")
def verify_email(token: str, session: Session = Depends(get_session)):
    """Verify email address using verification token"""
    try:
        # Find verification record
        verification = session.exec(select(EmailVerification).where(EmailVerification.token == token)).first()

        if not verification:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token")

        # Check if already verified
        if verification.is_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")

        # Check if token expired
        if verification.is_token_expired():
            # Delete expired verification
            session.delete(verification)
            session.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token expired")

        # Find the user
        user = session.exec(select(User).where(User.email == verification.email)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Mark user as verified
        user.is_email_verified = True
        user.email_verified_at = get_utc_now()

        # Mark verification as completed
        verification.is_verified = True
        verification.verified_at = get_utc_now()

        session.add(user)
        session.add(verification)
        session.commit()

        # Update the token to include verified status
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "verified": True}, expires_delta=access_token_expires
        )

        return {
            "success": True,
            "message": "Email verified successfully",
            "data": {"user": UserResponse.model_validate(user), "token": access_token},
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Verification error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Verification failed: {str(e)}")


@router.post("/resend-verification")
def resend_verification(email: str, session: Session = Depends(get_session)):
    """Resend verification email"""
    try:
        # Find the user
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            # Don't reveal if email exists or not for security
            return {"success": True, "message": "If the email exists, a verification email has been sent."}

        if user.is_email_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")

        # Invalidate old verification tokens
        old_verifications = session.exec(select(EmailVerification).where(EmailVerification.email == email)).all()

        for old_verification in old_verifications:
            session.delete(old_verification)

        # Create new verification token
        verification_token = EmailVerification.generate_token()
        email_verification = EmailVerification(email=email, token=verification_token, is_verified=False)
        session.add(email_verification)
        session.commit()

        # Send verification email
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        verification_url = f"{frontend_url}/verify-email?token={verification_token}"

        email_sent = email_service.send_verification_email(
            to_email=email, verification_token=verification_token, verification_url=verification_url
        )

        return {
            "success": True,
            "message": (
                "Verification email sent"
                if email_sent
                else "Verification email could not be sent. Please check SMTP configuration."
            ),
            "email_sent": email_sent,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Resend verification error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to resend verification: {str(e)}")


@router.get("/verification-status")
def get_verification_status(
    credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)
):
    """Get current user's verification status"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        user_id = uuid_lib.UUID(user_id_str)
        user = session.get(User, user_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return {
            "success": True,
            "data": {"is_verified": user.is_email_verified, "email_verified_at": user.email_verified_at},
        }
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
