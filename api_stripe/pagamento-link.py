# link_pagamento.py
from sqlalchemy.orm import Session
from database import get_db
from models import User

def get_client_by_email(email: str):
    db = next(get_db())
    try:
        user = db.query(User).filter(User.email == email).first()
        return user
    except Exception as e:
        print(f"Ocorreu um erro ao buscar o cliente: {e}")
    finally:
        db.close()
