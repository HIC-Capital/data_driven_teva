"""
Firebase client — authentication + profile persistence
======================================================

Uses pyrebase4 (client-side Firebase SDK) for:
  - Email/password sign-up and sign-in  (Firebase Authentication)
  - Reading and writing user profiles    (Firebase Realtime Database)

Profile schema stored at /users/{uid}:
{
  "role":        "student" | "professor",
  "first_name":  str,
  "last_name":   str,
  "email":       str,
  "level":       str,          # student only
  "programme":   str,          # student only
  "semester":    str,          # student only
  "language":    str,          # student only
  "prof_name":   str,          # professor only
  "prof_title":  str,          # professor only
  "prof_dept":   str,          # professor only
  "prof_email":  str,          # professor only
}

Callers get back plain dicts — no Firebase objects leak out.
"""
from __future__ import annotations

import streamlit as st

# ── Lazy singleton ──────────────────────────────────────────────────────────

_firebase = None
_auth     = None
_db       = None


def _init():
    """Initialise pyrebase once using secrets from .streamlit/secrets.toml."""
    global _firebase, _auth, _db
    if _firebase is not None:
        return True

    try:
        import pyrebase  # pyrebase4
    except ImportError:
        return False

    try:
        cfg = st.secrets.get("firebase", {})
        if not cfg or not cfg.get("apiKey"):
            return False

        _firebase = pyrebase.initialize_app({
            "apiKey":            cfg["apiKey"],
            "authDomain":        cfg["authDomain"],
            "databaseURL":       cfg["databaseURL"],
            "projectId":         cfg["projectId"],
            "storageBucket":     cfg.get("storageBucket", ""),
            "messagingSenderId": cfg.get("messagingSenderId", ""),
            "appId":             cfg.get("appId", ""),
        })
        _auth = _firebase.auth()
        _db   = _firebase.database()
        return True
    except Exception:
        return False


def is_configured() -> bool:
    """Return True if Firebase keys are present in secrets."""
    return _init()


# ── Authentication ──────────────────────────────────────────────────────────

def sign_up(email: str, password: str) -> dict:
    """
    Create a new Firebase Auth account.

    Returns {"uid": str, "email": str, "token": str} on success.
    Raises ValueError with a human-readable message on failure.
    """
    if not _init():
        raise ValueError("Firebase not configured — add [firebase] keys to .streamlit/secrets.toml")
    try:
        user = _auth.create_user_with_email_and_password(email, password)
        return {"uid": user["localId"], "email": user["email"], "token": user["idToken"]}
    except Exception as e:
        msg = str(e)
        if "EMAIL_EXISTS" in msg:
            raise ValueError("An account with this email already exists. Please log in.")
        if "WEAK_PASSWORD" in msg:
            raise ValueError("Password must be at least 6 characters.")
        if "INVALID_EMAIL" in msg:
            raise ValueError("Please enter a valid email address.")
        raise ValueError(f"Sign-up failed: {msg}")


def sign_in(email: str, password: str) -> dict:
    """
    Sign in with email and password.

    Returns {"uid": str, "email": str, "token": str} on success.
    Raises ValueError with a human-readable message on failure.
    """
    if not _init():
        raise ValueError("Firebase not configured — add [firebase] keys to .streamlit/secrets.toml")
    try:
        user = _auth.sign_in_with_email_and_password(email, password)
        return {"uid": user["localId"], "email": user["email"], "token": user["idToken"]}
    except Exception as e:
        msg = str(e)
        if "INVALID_PASSWORD" in msg or "INVALID_LOGIN_CREDENTIALS" in msg or "EMAIL_NOT_FOUND" in msg:
            raise ValueError("Incorrect email or password.")
        if "USER_DISABLED" in msg:
            raise ValueError("This account has been disabled.")
        raise ValueError(f"Login failed: {msg}")


# ── Profile persistence ─────────────────────────────────────────────────────

def save_profile(uid: str, token: str, data: dict) -> None:
    """
    Write profile data to /users/{uid} in Realtime Database.
    Silently skips if Firebase is not configured.
    """
    if not _init():
        return
    try:
        _db.child("users").child(uid).set(data, token)
    except Exception:
        pass  # never crash the app because of a DB write


def load_profile(uid: str, token: str) -> dict | None:
    """
    Read profile data from /users/{uid}.
    Returns None if not found or Firebase not configured.
    """
    if not _init():
        return None
    try:
        result = _db.child("users").child(uid).get(token)
        return result.val()
    except Exception:
        return None
