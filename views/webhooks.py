import streamlit as st
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import requests
import pandas as pd
import json


# Inicialização do FastAPI
app = FastAPI()


# Modelo para Webhook
class Webhook(BaseModel):
    id: Optional[int]  # ID do webhook, gerado automaticamente
    name: str          # Nome do webhook
    url: str           # URL onde o webhook será enviado
    event: str         # Evento que irá acionar o webhook
    enabled: bool      # Status do webhook (ativo ou inativo)

# Lista para armazenar os webhooks
webhooks_db = []
next_id = 1  # Simulação de ID incremental


@app.post("/webhooks/", response_model=Webhook)
async def create_webhook(webhook: Webhook):
    global next_id
    webhook.id = next_id
    webhooks_db.append(webhook)
    next_id += 1
    return webhook


@app.get("/webhooks/", response_model=List[Webhook])
async def list_webhooks():
    return webhooks_db


@app.get("/webhooks/{webhook_id}", response_model=Webhook)
async def get_webhook(webhook_id: int):
    for webhook in webhooks_db:
        if webhook.id == webhook_id:
            return webhook
    raise HTTPException(status_code=404, detail="Webhook not found")


@app.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: int):
    global webhooks_db
    webhooks_db = [webhook for webhook in webhooks_db if webhook.id != webhook_id]
    return {"message": "Webhook deleted successfully"}


async def show_webhooks():
    st.title("Sistema Flash Pagamentos")

    # Seção para criar um novo webhook
    st.header("Criar Webhook")
    with st.form(key='create_webhook'):
        name = st.text_input("Nome do Webhook", key='webhook_name')
        url = st.text_input("URL do Webhook", key='webhook_url')      # Chave única para a URL
        # Definindo uma lista de eventos que podem ser enviados para o Make
        eventos_disponiveis = [
            "Cliente Cadastrado",
            "Envio de Cobrança",
            "Cobrança Recebida",
            "Pagamento Recebido",
            "Link de Pagamento Criado",
            "Assinatura Criada",
        ]

        # Permitir que o usuário selecione um ou mais eventos
        eventos_selecionados = st.multiselect("Selecione os eventos", eventos_disponiveis, key='eventos_selecionados')
        enabled = st.checkbox("Ativo", value=True, key='webhook_active')
        submit_button = st.form_submit_button("Criar Webhook")


        if submit_button:
            webhook_data = {
                "name": name,  # Incluindo o nome na criação do webhook
                "url": url,
                "event": event,
                "enabled": enabled
            }
            response = requests.post(f"http://localhost:8000/webhooks/", json=webhook_data)  # Ajuste o BASE_URL conforme necessário
            if response.status_code == 200:
                st.success(f"Webhook criado com sucesso! ID: {response.json()['id']}")
            else:
                st.error("Erro ao criar webhook.")

        if submit_button:
            # Aqui você pode implementar a lógica para salvar o webhook e os eventos selecionados
            st.success(f"Webhook '{name}' criado com sucesso! URL: {url} e Eventos: {', '.join(eventos_selecionados)}")


    # Seção para listar webhooks
    st.header("Listar Webhooks")
    if st.button("Carregar Webhooks"):
        with st.spinner("Carregando lista de webhooks..."):
            response = requests.get(f"http://localhost:8000/webhooks/")  # Ajuste o BASE_URL conforme necessário
            if response.status_code == 200:
                webhooks = response.json()
                if webhooks:
                    df = pd.DataFrame(webhooks)
                    st.dataframe(df)  # Exibe a tabela de webhooks no Streamlit
                else:
                    st.warning("Nenhum webhook encontrado.")
            else:
                st.error("Erro ao carregar webhooks.")


# Modelo para o payload do webhook
class WebhookPayload(BaseModel):
    event: str  # Tipo de evento (ex: "PAYMENT_RECEIVED")
    data: dict  # Dados do evento

@app.post("/webhook/")
async def receive_webhook(payload: WebhookPayload):
    # Processar o payload recebido
    try:
        # Aqui você pode implementar a lógica para tratar o evento
        print(f"Evento recebido: {payload.event}")
        print(f"Dados: {json.dumps(payload.data, indent=2)}")

        # Retorne uma resposta de sucesso
        return {"message": "Webhook recebido com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar o webhook: {str(e)}")

# Inicie o servidor com: uvicorn webhook:app --reload
