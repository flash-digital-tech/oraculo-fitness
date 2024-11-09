import re
import streamlit as st
import requests  # pip install requests
import pandas as pd
import datetime
from streamlit_modal import Modal
from decouple import config


WEBHOOK_URL = config("WEBHOOK_URL")


def is_valid_email(email):
    # Basic regex pattern for email validation
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_pattern, email) is not None


def contact_form():
    with st.form("contact_form"):
        name = st.text_input("Nome e Sobrenome")
        email = st.text_input("E-mail")
        message = st.text_area("Envie uma mensagem")
        submit_button = st.form_submit_button("ENVIAR")

    if submit_button:
        if not WEBHOOK_URL:
            st.error("Email service is not set up. Please try again later.", icon="📧")
            st.stop()

        if not name:
            st.error("Please provide your name.", icon="🧑")
            st.stop()

        if not email:
            st.error("Please provide your email address.", icon="📨")
            st.stop()

        if not is_valid_email(email):
            st.error("Please provide a valid email address.", icon="📧")
            st.stop()

        if not message:
            st.error("Please provide a message.", icon="💬")
            st.stop()

        # Prepare the data payload and send it to the specified webhook URL
        data = {"email": email, "name": name, "message": message}
        response = requests.post(WEBHOOK_URL, json=data)

        if response.status_code == 200:
            st.success("A sua mensagem foi enviada com sucesso! 🎉", icon="🚀")
        else:
            st.error("Desculpe-me, parece que houve um problema no envio da sua mensagem", icon="😨")



def cadastro_pedido():
    with st.form("cadastro_pedido"):
        name = st.text_input("Nome")
        whatsapp = st.text_input("WhatsApp")
        endereco = st.text_input("Endereço")
        message = st.text_area("Envie uma observação")
        submit_button = st.form_submit_button("ENVIAR")

    if submit_button:
        if not WEBHOOK_URL:
            st.error("Email service is not set up. Please try again later.", icon="📧")
            st.stop()

        if not name:
            st.error("Qual o seu nome?", icon="🧑")
            st.stop()

        if not whatsapp:
            st.error("Digite seu WhatsApp.", icon="📨")
            st.stop()

        if not endereco:
            st.error("Digite seu endereço com o nome do bairro.", icon="📨")
            st.stop()

        if not message:
            st.error("Deixe sua observação caso tenha.", icon="💬")
            st.stop()

        # Prepare the data payload and send it to the specified webhook URL
        data = {"Nome": name, "WhatsApp": whatsapp, "Endereço": endereco}
        response = requests.post(WEBHOOK_URL, json=data)

        if response.status_code == 200:
            st.success("A sua mensagem foi enviada com sucesso! 🎉", icon="🚀")
        else:
            st.error("Desculpe-me, parece que houve um problema no envio da sua mensagem", icon="😨")


def cadastrar_cliente():
    st.title('Cadastro para pedido.')

    # Criação do modal
    modal = Modal("CONFIRMAÇÃO DE DADOS", key="modal_key")

    with st.form('cliente_info'):
        nome = st.text_input('Qual o seu nome? ')
        whatsapp = st.text_input('Digite seu WhatsApp: ')
        endereco = st.text_input('Informe seu endereço com bairro e cep: ')
        submitted = st.form_submit_button("CONFIRMAR DADOS")

    if submitted:
        cliente_info = {
            "Nome": nome,
            "WhatsApp": whatsapp,
            "Endereço": endereco,
            "Horário": datetime.datetime.now().strftime("%d-%m-%y %H:%M:%S")
        }

        # Aqui você pode abrir o modal com a confirmação
        modal.open()  # Método para abrir o modal

        st.write('Dados Coletados')
        st.write(cliente_info)

        df = pd.DataFrame([cliente_info])
        df.to_excel("DadosEntrega.xlsx", index=False, header=False, mode="a")

        st.success('Dados enviados com sucesso!')




