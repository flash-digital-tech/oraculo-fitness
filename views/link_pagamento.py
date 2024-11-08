import streamlit as st
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from httpx import AsyncClient
import pandas as pd
from configuracao import ASAAS_API_KEY, BASE_URL  # Importando as configurações necessárias
from typing import Optional
from datetime import datetime, timedelta


app = FastAPI()


class LinkPagamento(BaseModel):
    name: str
    billingType: str
    chargeType: str
    endDate: str  # Deve ser uma string
    dueDateLimitDays: int
    status: str  # Status do link (ex: ACTIVE, INACTIVE)
    value: float  # Valor do pagamento
    description: Optional[str]  # Descrição do pagamento
    createdAt: str  # Deve ser uma string
    dueDate: str  # Deve ser uma string
    customerId: str  # ID do cliente associado ao link


async def criar_link_pagamento(link: LinkPagamento):
    async with AsyncClient() as client:
        try:
            response = await client.post(
                f'{BASE_URL}/paymentLinks',
                headers={'access_token': ASAAS_API_KEY},
                json=link.dict()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao criar link de pagamento: {e}")
            if hasattr(e, 'response'):
                st.error(f"Detalhes do erro: {e.response.text}")


async def fetch_payment_links():
    async with AsyncClient() as client:
        response = await client.get(
            f'{BASE_URL}/paymentLinks',
            headers={'access_token': ASAAS_API_KEY}
        )
        response.raise_for_status()  # Levanta um erro se a resposta não for bem-sucedida
        return response.json()["data"]  # Retorna apenas os dados dos links de pagamento

@app.post("/links-pagamento/")
async def create_payment_link(link: LinkPagamento):
    response = await criar_link_pagamento(link)
    return {"id": response["id"]}

@app.get("/links-pagamento/")
async def get_payment_links():
    try:
        links_pagamento = await fetch_payment_links()
        if links_pagamento:
            data = []
            for link in links_pagamento:
                data.append({
                    'Nome do Link': link['name'],
                    'Valor': link['value'],
                    'Forma de Pagamento': link['billingType'],
                    'chargeType': link['chargeType'],
                    'dueDateLimitDays': link['dueDateLimitDays'],
                    'endDate': link['endDate'],  # Usa .get() para evitar KeyError
                    'status': link.get('status', 'N/A')
                })
            df = pd.DataFrame(data)
            return df.to_dict("records")
        else:
            return {"message": "Nenhum link de pagamento encontrado."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar links de pagamento: {e}")

async def show_pagamento_links():
    st.title("Sistema Flash Pagamentos")

    # Seção para criar um novo link de pagamento
    st.header("Criar Link de Pagamento")
    with st.form(key='create_link_pagamento'):
        name = st.text_input("Nome do Link", key='name')
        value = st.number_input("Valor do Pagamento", min_value=0.0, format="%.2f", key='value')
        billingType = st.selectbox("Tipo de Pagamento", options=["CARTAO", "BOLETO", "DEBITO", "PIX"], key='billingType')
        chargeType = st.selectbox("Forma de Cobrança", options=["MENSAL", "INSTANTANEO", "SEMANAL"], key='chargeType')
        description = st.text_input("Descrição (opcional)", key='description')
        submit_button = st.form_submit_button("Criar Link de Pagamento")

        if submit_button:
            endDate = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")  # Formata a data como string
            dueDateLimitDays = 5  # Limite de dias para o vencimento do link
            status = "ACTIVE"  # Status do link (ativo)
            createdAt = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # Formata a data como string
            dueDate = (datetime.now() + timedelta(days=dueDateLimitDays)).strftime("%Y-%m-%d")  # Formata a data como string
            customerId = "123456789"  # ID do cliente associado ao link

            novo_link = LinkPagamento(
                name=name,
                value=value,
                billingType=billingType,
                chargeType=chargeType,
                description=description,
                endDate=endDate,
                dueDateLimitDays=dueDateLimitDays,
                status=status,
                createdAt=createdAt,
                dueDate=dueDate,
                customerId=customerId
            )

            response = await create_payment_link(novo_link)
            st.success(f"Link de pagamento criado com sucesso! ID: {response['id']}")

    # Seção para listar os links de pagamento
    st.header("Links de Pagamento")
    try:
        links_pagamento = await fetch_payment_links()
        if links_pagamento:
            data = []
            for link in links_pagamento:
                data.append({
                    'Nome do Link': link['name'],
                    'Valor': link['value'],
                    'Forma de Pagamento': link['billingType'],
                    'chargeType': link['chargeType'],
                    'dueDateLimitDays': link['dueDateLimitDays'],
                    'endDate': link['endDate'],  # Usa .get() para evitar KeyError
                    'status': link.get('status', 'N/A')
                })
            df = pd.DataFrame(data)
            st.write(df)
        else:
            st.write("Nenhum link de pagamento encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar links de pagamento: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
