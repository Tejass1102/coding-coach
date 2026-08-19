"""
JWT Authentication dependency for FastAPI.

Uses Supabase's built-in auth.get_user() to validate the Bearer token.
This works with both the legacy HS256 key AND the new ECC (P-256) key automatically —
no JWT secret needed in .env.

Usage: Add `current_user: dict = Depends(get_current_user)` to any route.
"""

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

security = HTTPBearer()


def _derive_username(user) -> str:
    """
    Derives a display username from the Supabase user object.
    Priority: user_metadata.username → full_name (Google OAuth) → name → email prefix
    """
    meta = user.user_metadata or {}
    return (
        meta.get("username")
        or meta.get("full_name")
        or meta.get("name")
        or (user.email.split("@")[0] if user.email else "user")
    )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Validates the Bearer JWT token by calling Supabase Auth.
    Returns the user object on success, raises 401 on failure.
    """
    token = credentials.credentials

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.auth.get_user(token)

        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Return a plain dict with the key user fields
        user = response.user
        return {
            "id": user.id,
            "email": user.email,
            "username": _derive_username(user),
            "role": user.role,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
