"""Rotas de autenticação (cadastro, login e listagem de usuários)."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserLogin, UserRegister
from app.security import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _public_user(user: User) -> dict:
    """Remove o campo password da resposta para não expor dados sensíveis."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.post("/register", response_model=dict, status_code=201)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Cadastra um novo usuário.

    Body:
    {
        "name": "Nome do usuário",
        "email": "usuario@email.com",
        "password": "123456"
    }

    Resposta: dados públicos do usuário, um token de sessão e o tempo de validade.
    """
    email = payload.email.strip().lower()

    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="O nome é obrigatório.")

    if len(payload.name.strip()) > 120:
        raise HTTPException(
            status_code=400,
            detail="O nome deve ter no máximo 120 caracteres.",
        )

    if len(payload.password) < 6:
        raise HTTPException(
            status_code=400, detail="A senha deve ter pelo menos 6 caracteres."
        )

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=409, detail="Já existe um usuário com este e-mail."
        )

    user = User(
        name=payload.name.strip(),
        email=email,
        password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        **_public_user(user),
        "token": f"token-{user.id}",
        "expires_in": 86400,
        "message": "Usuário cadastrado com sucesso!",
    }


@router.post("/login", response_model=dict)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Realiza o login de um usuário existente.

    Body:
    {
        "email": "usuario@email.com",
        "password": "123456"
    }
    """
    email = payload.email.strip().lower()

    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")

    return {
        **_public_user(user),
        "token": f"token-{user.id}",
        "expires_in": 86400,
        "message": "Login realizado com sucesso!",
    }


@router.get("/users", response_model=List[dict])
def list_users(db: Session = Depends(get_db)):
    """
    Retorna a lista de usuários cadastrados (sem senhas).
    Útil para depuração em ambiente de desenvolvimento.
    """
    return [_public_user(u) for u in db.query(User).all()]
