# app.py
import streamlit as st
import stripe
import requests
import pandas as pd
from pydantic import BaseModel
from decouple import config

# Configure sua chave secreta da API do Stripe
stripe.api_key = config("stripe.api_key")  # Corrigido para usar a chave correta

# URL base da API FastAPI
API_URL = "http://127.0.0.1:8000"

# Modelos de dados
class Plano(BaseModel):
    nome: str
    valor: int  # Valor em centavos
    intervalo: str
    moeda: str = "usd"

def criar_plano(plano: Plano):
    try:
        plano_criado = stripe.Plan.create(
            amount=plano.valor,
            currency=plano.moeda,
            interval=plano.intervalo,
            product={"name": plano.nome},
        )
        return {"id": plano_criado.id, "message": "Plano criado com sucesso."}
    except Exception as e:
        return {"detail": str(e)}  # Retorna o erro como parte da resposta

# Função para criar uma assinatura
def criar_assinatura(cliente_id, plano_id):
    response = requests.post(f"{API_URL}/assinaturas/", json={
        "cliente_id": cliente_id,
        "plano_id": plano_id
    })
    return response.json()

# Função para listar assinaturas
def listar_assinaturas(cliente_id):
    response = requests.get(f"{API_URL}/assinaturas/{cliente_id}")
    return response.json()

# Função para cancelar uma assinatura
def cancelar_assinatura(assinatura_id):
    response = requests.delete(f"{API_URL}/assinaturas/", json={
        "assinatura_id": assinatura_id
    })
    return response.json()

# Interface do Streamlit
st.title("Gerenciamento de Pagamentos Recorrentes")

# Criar Plano
st.header("Criar Plano")
with st.form(key='form_criar_plano'):
    nome = st.text_input("Nome do Plano")
    valor = st.number_input("Valor (em centavos)", min_value=0)
    intervalo = st.selectbox("Intervalo", ["month", "year"])
    moeda = st.selectbox("Moeda", ["usd", "brl"])
    submit_button = st.form_submit_button(label='Criar Plano')

    if submit_button:
        plano = Plano(nome=nome, valor=valor, intervalo=intervalo, moeda=moeda)  # Cria um objeto Plano
        resultado = criar_plano(plano)  # Passa o objeto Plano para a função
        if 'id' in resultado:
            st.success(f"Plano criado: {resultado['id']}")
        else:
            st.error("Erro ao criar plano: " + resultado.get('detail', 'Erro desconhecido'))

# Criar Assinatura
st.header("Criar Assinatura")
with st.form(key='form_criar_assinatura'):
    cliente_id = st.text_input("ID do Cliente")
    plano_id = st.text_input("ID do Plano")
    submit_button_assinatura = st.form_submit_button(label='Criar Assinatura')

    if submit_button_assinatura:
        resultado_assinatura = criar_assinatura(cliente_id, plano_id)
        if 'id' in resultado_assinatura:
            st.success(f"Assinatura criada: {resultado_assinatura['id']}")
        else:
            st.error("Erro ao criar assinatura: " + resultado_assinatura.get('detail', 'Erro desconhecido'))

# Listar Assinaturas
st.header("Listar Assinaturas")
cliente_id_listar = st.text_input("ID do Cliente para listar assinaturas")
if st.button("Listar Assinaturas"):
    if cliente_id_listar:
        assinaturas = listar_assinaturas(cliente_id_listar)
        if assinaturas:
            df = pd.DataFrame(assinaturas)
            st.dataframe(df)
        else:
            st.warning("Nenhuma assinatura encontrada.")

# Cancelar Assinatura
st.header("Cancelar Assinatura")
with st.form(key='form_cancelar_assinatura'):
    assinatura_id = st.text_input("ID da Assinatura a Cancelar")
    submit_button_cancelar = st.form_submit_button(label='Cancelar Assinatura')

    if submit_button_cancelar:
        resultado_cancelar = cancelar_assinatura(assinatura_id)
        if 'message' in resultado_cancelar:
            st.success(resultado_cancelar['message'])
        else:
            st.error("Erro ao cancelar assinatura: " + resultado_cancelar.get('detail', 'Erro desconhecido'))
