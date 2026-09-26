from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.core.security import decode_access_token
from app.database.database import get_db
from sqlalchemy.orm import Session

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: Optional[str] = payload.get("sub")
    role: Optional[str] = payload.get("role")
    
    if user_id is None or role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": user_id, "role": role}


async def get_current_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get the current authenticated user, ensuring they are an admin."""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    return current_user


async def get_current_employee(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get the current authenticated user, ensuring they are an employee."""
    if current_user["role"] not in ["employee", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    return current_user