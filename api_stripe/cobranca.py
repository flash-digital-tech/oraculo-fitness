# cobranca.py
from sqlalchemy.orm import Session
from database import get_db
from models import User


def update_payment(email: str, amount_paid: float):
    db = next(get_db())
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.amount_paid += amount_paid
            db.commit()
            print(f"Pagamento atualizado para o cliente {email}.")
        else:
            print("Cliente não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao atualizar o pagamento: {e}")
    finally:
        db.close()
