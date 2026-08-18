"""
Auth routes — login, signup, logout.

These endpoints proxy Supabase Auth so the frontend can call your FastAPI
backend instead of Supabase directly (optional, but keeps auth centralised).
The frontend can also call Supabase directly via the JS SDK.
"""

import os
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client

router = APIRouter(prefix="/auth", tags=["auth"])

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ── Request models ────────────────────────────────────────────────────────────

class AuthRequest(BaseModel):
    email: EmailStr
    password: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/login")
def login(body: AuthRequest):
    """Sign in with email + password. Returns access_token and user info."""
    supabase = get_supabase()
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
        session = response.session
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/signup")
def signup(body: AuthRequest):
    """Create a new account with email + password."""
    supabase = get_supabase()
    try:
        response = supabase.auth.sign_up(
            {"email": body.email, "password": body.password}
        )
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sign up failed",
            )
        return {
            "message": "Account created. Check your email to confirm your account.",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/logout")
def logout():
    """Sign out the current user (handled client-side via Supabase SDK)."""
    # Supabase JWT logout is handled client-side.
    # The access token expires automatically. This endpoint is a no-op placeholder.
    return {"message": "Logged out successfully"}
