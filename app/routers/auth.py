"""Rotas de autenticação: cadastro, login e sessão atual."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import JWT_EXPIRE_SECONDS
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import AuthResponse, UserLogin, UserPublic, UserRegister
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _public_user(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at,
    }


def _auth_response(user: User, message: str) -> dict:
    token = create_access_token(user.id)
    return {
        **_public_user(user),
        # "token" mantém compatibilidade com o frontend anterior.
        "token": token,
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRE_SECONDS,
        "message": message,
    }


@router.post("/register", response_model=AuthResponse, status_code=201)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    """Cadastra um usuário e já inicia uma sessão autenticada."""
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=409, detail="Já existe um usuário com este e-mail."
        )

    user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Já existe um usuário com este e-mail."
        ) from None
    db.refresh(user)
    return _auth_response(user, "Usuário cadastrado com sucesso!")


@router.post("/login", response_model=AuthResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """Valida as credenciais e retorna um token Bearer com expiração."""
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")
    return _auth_response(user, "Login realizado com sucesso!")


@router.get("/me", response_model=UserPublic)
def get_session_user(current_user: User = Depends(get_current_user)):
    """Retorna o usuário identificado pelo token Bearer."""
    return _public_user(current_user)
