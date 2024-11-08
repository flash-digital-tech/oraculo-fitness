# database.py
import sqlalchemy as sa
from sqlalchemy.future.engine import Engine
from sqlalchemy.orm import sessionmaker
from typing import Optional
from sqlalchemy.orm import Session
from decouple import config
from api_stripe.models.model_base import ModelBase


__engine: Optional[Engine] = None

def create_conect() -> Engine:
    global __engine

    if __engine:
        return __engine  # Retorna a conexão existente

    try:
        conex_str = "mysql+mysqldb://root:root@localhost:3306/fitnes-dados"
        __engine = sa.create_engine(url=conex_str, echo=False)

        print("Conexão bem-sucedida ao MySQL")
        return __engine
    except sa.exc.SQLAlchemyError as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

# Chame a função para criar a conexão
engine = create_conect()

# Criar uma sessão
if engine:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session: Session = SessionLocal()
    print("Sessão criada com sucesso.")
else:
    print("Falha ao criar a sessão.")


def create_session() -> Session:
    global __engine
    if not __engine:
        create_conect()

    __session = sessionmaker(__engine, expire_on_commit=False, class_=Session)
    session: Session = __session()
    return session

def create_tables() -> None:
    global __engine
    if not __engine:
        create_conect()

    import api_stripe.models.__all_models
    ModelBase.metadata.drop_all(__engine)
    ModelBase.metadata.create_all(__engine)

