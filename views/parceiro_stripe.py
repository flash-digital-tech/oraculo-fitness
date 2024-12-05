import asyncio
import streamlit as st
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import httpx
from key_config import API_KEY_STRIPE, URL_BASE

app = FastAPI()

# Modelo de Parceiro
class ParceiroCreate(BaseModel):
    nome: str
    email: str
    telefone: str

class ParceiroResponse(BaseModel):
    id: str
    nome: str
    email: str
    telefone: str

async def criar_parceiro_no_stripe(parceiro: ParceiroCreate):
    url = f"{URL_BASE}/accounts"
    headers = {
        "Authorization": f"Bearer {API_KEY_STRIPE}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "type": "express",
        "country": "BR",
        "email": parceiro.email,
        "capabilities[transfers]": "active",
        "individual[first_name]": parceiro.nome.split()[0],
        "individual[last_name]": parceiro.nome.split()[1] if len(parceiro.nome.split()) > 1 else "",
        "individual[phone]": parceiro.telefone,
        "business_type": "individual"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

@app.post("/parceiros", response_model=ParceiroResponse)
async def api_create_parceiro(parceiro: ParceiroCreate):
    try:
        novo_parceiro = await criar_parceiro_no_stripe(parceiro)
        return ParceiroResponse(
            id=novo_parceiro['id'],
            nome=parceiro.nome,
            email=parceiro.email,
            telefone=parceiro.telefone
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def fetch_parceiros(offset: int = 0, limit: int = 100):
    try:
        # Buscando a lista de parceiros com limite e starting_after
        parceiros = stripe.Account.list(limit=limit, starting_after=None)  # Ajustado para refletir a API correta

        # Verifica se os dados de parceiros estão disponíveis
        if not parceiros['data']:
            raise HTTPException(status_code=404, detail="Nenhum parceiro encontrado.")

        return [
            ParceiroResponse(
                id=parceiro['id'],
                nome=parceiro.get('business_profile', {}).get('name', 'Nome não disponível'),
                email=parceiro.get('email', 'Email não disponível'),
                telefone=parceiro.get('metadata', {}).get('telefone', ''),  # Incluindo telefone
            ) for parceiro in parceiros['data']
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/parceiros", response_model=list[ParceiroResponse])
async def api_fetch_parceiros(offset: int = 0, limit: int = 100):
    return await fetch_parceiros(offset, limit)

async def handle_fetch_parceiros(offset, limit):
    try:
        parceiros = await fetch_parceiros(offset=offset, limit=limit)
        if parceiros:
            data = []
            for parceiro in parceiros:
                data.append({
                    'ID': parceiro.id,
                    'Nome': parceiro.nome,
                    'E-mail': parceiro.email,
                    'Telefone': parceiro.telefone,  # Incluindo o telefone na exibição
                })
            df = pd.DataFrame(data)
            st.dataframe(df)  # Exibe a tabela de parceiros no Streamlit
        else:
            st.warning("Nenhum parceiro encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar parceiros: {e}")


# Streamlit Interface
def showParceiroStripe():
    st.title("Sistema Flash Pagamentos")

    st.header("Criar Novo Parceiro")

    if 'nome' not in st.session_state:
        st.session_state.nome = ""
    if 'email' not in st.session_state:
        st.session_state.email = ""
    if 'telefone' not in st.session_state:
        st.session_state.telefone = ""

    with st.form(key='form_parceiro'):
        st.session_state.nome = st.text_input("Nome:", value=st.session_state.nome)
        st.session_state.email = st.text_input("E-mail:", value=st.session_state.email)
        st.session_state.telefone = st.text_input("Telefone:", value=st.session_state.telefone)

        submit_button = st.form_submit_button("CRIAR PARCEIRO!")

        if submit_button:
            parceiro = ParceiroCreate(
                nome=st.session_state.nome,
                email=st.session_state.email,
                telefone=st.session_state.telefone
            )
            try:

                resultado = asyncio.create_task(api_create_parceiro(parceiro))
                st.success(f"Parceiro {resultado.nome} criado com sucesso!")

                st.session_state.nome = ""
                st.session_state.email = ""
                st.session_state.telefone = ""

            except Exception as e:
                st.error(f"Erro ao criar parceiro: {e}")

    # Seção para listar parceiros
st.header("Listar Parceiros")
offset = st.number_input("Offset", min_value=0, value=0)
limit = st.number_input("Limite", min_value=1, max_value=100, value=10)

if st.button("Carregar Lista de Parceiros"):
    try:
        parceiros = asyncio.create_task(fetch_parceiros(offset=offset, limit=limit))  # Chamada da função
        if parceiros:
            data = []
            for parceiro in parceiros:
                data.append({
                    'ID': parceiro.id,
                    'Nome': parceiro.nome,
                    'E-mail': parceiro.email,
                    'Telefone': parceiro.telefone,  # Incluindo telefone
                })
            df = pd.DataFrame(data)
            st.dataframe(df)  # Exibe a tabela de parceiros no Streamlit
        else:
            st.warning("Nenhum parceiro encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar parceiros: {e}")
