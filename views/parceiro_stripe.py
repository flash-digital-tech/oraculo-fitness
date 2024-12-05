import streamlit as st
import pandas as pd
import os
import stripe
import httpx
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from key_config import API_KEY_STRIPE, URL_BASE

# Configuração da API do Stripe

app = FastAPI()

# Inicializa a lista para armazenar os parceiros
parceiros = []

class ParceiroStripe(BaseModel):
    nome: str
    documento: str
    email: str
    whatsapp: str

async def criar_parceiro_stripe(nome: str, documento: str, email: str, whatsapp: str):
    """Cria uma subconta no Stripe de forma assíncrona."""
    try:
        # Criação da subconta usando a API do Stripe
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.stripe.com/v1/accounts",
                headers={
                    "Authorization": f"Bearer sua_chave_secreta_do_stripe",  # Insira sua chave secreta aqui
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "type": "express",
                    "country": "BR",
                    "email": email,
                    "business_type": "individual",
                    "capabilities[card_payments][requested]": "true",
                    "capabilities[transfers][requested]": "true",
                    "business_profile[name]": nome,
                    "business_profile[support_email]": email,
                    "business_profile[support_phone]": whatsapp,
                    "external_account[object]": "bank_account",
                    "external_account[country]": "BR",
                    "external_account[currency]": "BRL",
                    "external_account[account_number]": documento,  # CPF ou CNPJ
                    "external_account[routing_number]": "12345678",  # Número de roteamento fictício
                }
            )

        response.raise_for_status()  # Levanta um erro se a resposta não for 200
        return response.json()  # Retorna os dados da subconta criada

    except Exception as e:
        st.error(f"Ocorreu um erro ao criar a subconta: {str(e)}")


def showParceiroStripe():
    st.title("Sistema Flash Pagamentos")

    # Seção para criar um novo parceiro
    st.header("Criar Novo Parceiro")

    # Inicializa os campos no session_state se não existirem
    if 'name' not in st.session_state:
        st.session_state.name = ""
    if 'documento' not in st.session_state:
        st.session_state.documento = ""
    if 'email' not in st.session_state:
        st.session_state.email = ""
    if 'whatsapp' not in st.session_state:
        st.session_state.whatsapp = ""

    # Formulário para cadastro de parceiro
    with st.form(key='form_parceiro'):
        name = st.text_input("Nome:", value=st.session_state.name)
        documento = st.text_input("CPF/CNPJ", value=st.session_state.documento)
        email = st.text_input("E-mail", value=st.session_state.email)
        whatsapp = st.text_input(label="WhatsApp", placeholder='Exemplo: 31900001111', value=st.session_state.whatsapp)

        # Botão para enviar os dados do formulário
        submit_button = st.form_submit_button("CRIAR PARCEIRO!")

        if submit_button:
            # Chama a função assíncrona para criar o parceiro
            try:
                asyncio.create_task(criar_parceiro_stripe(st.session_state.name, st.session_state.documento, st.session_state.email, st.session_state.whatsapp))
                parceiros.append({
                    'name': st.session_state.name,
                    'documento': st.session_state.documento,
                    'email': st.session_state.email,
                    'whatsapp': st.session_state.whatsapp
                })
                st.success("Parceiro cadastrado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao cadastrar parceiro: {str(e)}")

    # Seção para listar parceiros
    st.header("Listar Parceiros")
    if st.button("Carregar Lista de Parceiros"):
        if parceiros:
            df = pd.DataFrame(parceiros)
            st.dataframe(df)  # Exibe a tabela de parceiros no Streamlit
        else:
            st.warning("Nenhum parceiro encontrado.")
