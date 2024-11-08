import streamlit as st
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from httpx import AsyncClient
import pandas as pd
from configuracao import ASAAS_API_KEY, BASE_URL  # Importando as configurações necessárias
from typing import Optional
from datetime import datetime, date
from autentic.authentications import setup_authentication


app = FastAPI()


# Modelo de Cliente
class Cliente(BaseModel):
    nome: str
    email: str
    cpf_cnpj: str
    whatsapp: str
    endereco: str
    cep: str  # O CEP deve ser uma string para incluir zeros à esquerda
    bairro: str
    cidade: str


async def create_customer(customer: Cliente):
    async with AsyncClient() as client:
        response = await client.post(
            f'{BASE_URL}/customers',
            json={
                "name": customer.nome,
                "email": customer.email,
                "cpf": customer.cpf_cnpj,
                "phone": customer.whatsapp,
                "address": customer.endereco,
                "postalCode": customer.cep,
                "district": customer.bairro,
                "city": customer.cidade
            },
            headers={'access_token': ASAAS_API_KEY}
        )
        response.raise_for_status()
        return response.json()


async def fetch_customers(offset: int = 0, limit: int = 100, name: Optional[str] = None, email: Optional[str] = None):
    async with AsyncClient() as client:
        params = {
            "offset": offset,
            "limit": limit,
            "name": name,
            "email": email
        }
        response = await client.get(
            f'{BASE_URL}/customers',
            headers={'access_token': ASAAS_API_KEY},
            params={k: v for k, v in params.items() if v is not None}  # Filtra parâmetros None
        )
        response.raise_for_status()
        return response.json()["data"]  # Retorna apenas os dados dos clientes


async def show_create_customer():
    st.title("Sistema Flash Pagamentos")
    st.header("Criar Novo Cliente")

    # Inicializa os campos no session_state se não existirem
    if 'nome' not in st.session_state:
        st.session_state.nome = ""
    if 'documento' not in st.session_state:
        st.session_state.documento = ""
    if 'email' not in st.session_state:
        st.session_state.email = ""
    if 'whatsapp' not in st.session_state:
        st.session_state.whatsapp = ""
    if 'endereco' not in st.session_state:
        st.session_state.endereco = ""
    if 'cep' not in st.session_state:
        st.session_state.cep = ""
    if 'bairro' not in st.session_state:
        st.session_state.bairro = ""
    if 'city' not in st.session_state:
        st.session_state.city = ""

    # Formulário para cadastro de cliente
    with st.form(key='form_cliente'):
        # Cria colunas para organizar os campos
        col1, col2 = st.columns(2)  # Colunas para Nome e WhatsApp/Email
        col3, col4 = st.columns(2)  # Colunas para Endereço e Bairro/CEP

        # Coleta de dados do cliente
        with col1:
            st.session_state.nome = st.text_input("Nome", value=st.session_state.nome)  # Nome em uma coluna
            st.session_state.documento = st.text_input("CPF/CNPJ", value=st.session_state.documento)
        with col2:
            st.session_state.email = st.text_input("E-mail", value=st.session_state.email)  # E-mail e WhatsApp em uma coluna
            st.session_state.whatsapp = st.text_input(label="WhatsApp", placeholder='Exemplo: 31900001111', value=st.session_state.whatsapp)

        with col3:
            st.session_state.endereco = st.text_input("Endereço", value=st.session_state.endereco)  # Endereço em uma coluna
            st.session_state.bairro = st.text_input("Bairro", value=st.session_state.bairro)
        with col4:
            st.session_state.cep = st.text_input("CEP", value=st.session_state.cep)
            st.session_state.city = st.text_input("Cidade:", value=st.session_state.city)

        # Botão para enviar os dados do formulário
        submit_button = st.form_submit_button("CRIAR CLIENTE!")

        if submit_button:
            cliente = Cliente(
                nome=st.session_state.nome,
                email=st.session_state.email,
                cpf_cnpj=st.session_state.documento,
                whatsapp=st.session_state.whatsapp,
                endereco=st.session_state.endereco,
                cep=st.session_state.cep,
                bairro=st.session_state.bairro,
                cidade=st.session_state.city
            )
            try:
                resultado = await create_customer(cliente)  # Chame a função assíncrona diretamente
                st.success(f"Cliente {resultado['name']} criado com sucesso!")

                # Limpa os campos do formulário
                st.session_state.nome = ""
                st.session_state.documento = ""
                st.session_state.email = ""
                st.session_state.whatsapp = ""
                st.session_state.endereco = ""
                st.session_state.cep = ""
                st.session_state.bairro = ""
                st.session_state.city = ""

            except Exception as e:
                st.error(f"Erro ao criar cliente: {e}")

    st.header("Listar Clientes")
    offset = st.number_input("Offset", min_value=0, value=0)
    limit = st.number_input("Limite", min_value=1, max_value=100, value=10)
    name = st.text_input("Filtrar por Nome (opcional)")
    email = st.text_input("Filtrar por E-mail (opcional)")

    if st.button("Carregar Lista de Clientes"):
        try:
            clientes = await fetch_customers(offset=offset, limit=limit, name=name, email=email)
            if clientes:
                data = []
                for cliente in clientes:
                    data.append({
                        'ID': cliente['id'],
                        'Nome': cliente['name'],
                        'E-mail': cliente['email'],
                        'CPF/CNPJ': cliente.get('cpf', 'N/A'),  # CPF pode não estar presente
                    })
                df = pd.DataFrame(data)
                st.dataframe(df)  # Exibe a tabela de clientes no Streamlit
            else:
                st.warning("Nenhum cliente encontrado.")
        except Exception as e:
            st.error(f"Erro ao carregar clientes: {e}")

    
