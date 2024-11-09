import streamlit as st
import os
from transformers import AutoTokenizer
import base64
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import pandas as pd
import io



import replicate
from replicate import models
from langchain.llms import Replicate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings, SentenceTransformerEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from autentic.authentications import setup_authentication
from decouple import config


# --- PAGE SETUP ---
authenticator = setup_authentication()

if 'authentication_status' in st.session_state:
    if st.session_state['authentication_status']:
        authenticator.logout()
        st.write(f'Welcome *{st.session_state["name"]}*')
        st.title('Some content')  # Altere para o conteúdo específico da página
    elif st.session_state['authentication_status'] is False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] is None:
        st.warning('Please enter your username and password')

# --- LOGIN ---

# --- CONTINUAR COM O CÓDIGO DA PÁGINA ---

app = FastAPI()


# --- Verifica se o token da API está nos segredos ---
if 'REPLICATE_API_TOKEN':
    replicate_api = config('REPLICATE_API_TOKEN')
else:
    # Se a chave não está nos segredos, define um valor padrão ou continua sem o token
    replicate_api = None

# Essa parte será executada se você precisar do token em algum lugar do seu código
if replicate_api is None:
    # Se você quiser fazer algo específico quando não há token, você pode gerenciar isso aqui
    # Por exemplo, configurar uma lógica padrão ou deixar o aplicativo continuar sem mostrar nenhuma mensagem:
    st.warning('Um token de API é necessário para determinados recursos.', icon='⚠️')



################################################# ENVIO DE E-MAIL ####################################################
############################################# PARA CONFIRMAÇÃO DE DADOS ##############################################

# Função para enviar o e-mail
def enviar_email(destinatario, assunto, corpo):
    remetente = "mensagem@flashdigital.tech"  # Insira seu endereço de e-mail
    senha = "sua_senha"  # Insira sua senha de e-mail

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'plain'))

    try:
        server = smtplib.SMTP('mail.flashdigital.tech', 587)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()
        st.success("E-mail enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")

    # Enviando o e-mail ao pressionar o botão de confirmação
    if st.button("DADOS CONFIRMADO"):
        # Obter os dados salvos em st.session_state
        nome = st.session_state.user_data["name"]
        whatsapp = st.session_state.user_data["whatsapp"]
        email = st.session_state.user_data["email"]

        # Construindo o corpo do e-mail
        corpo_email = f"""
        Olá {nome},

        Segue a confirmação dos dados:
        - Nome: {nome}
        - WhatsApp: {whatsapp}
        - E-mail: {email}

        Obrigado pela confirmação!
        """

        # Enviando o e-mail
        enviar_email(email, "Confirmação de dados", corpo_email)


#######################################################################################################################

system_prompt = f'''Você é um médico formado e reconhecido mundialmente, seu network é extenso e tem uma base de dados 
de médicos específica com informações precisas de cada um deles. Você Responderá às perguntas com base nos dados.

Os dados coletados são:
{', '.join([f"Dr. {medico.get('nome', 'Não informado')} - CRM: {medico.get('crm', 'Não informado')}, Site: {medico.get('site', 'Não informado')}, Redes Sociais: {medico.get('redes_sociais', 'Não informado')}, Endereço: {medico.get('endereco', 'Não informado')}, Telefone: {medico.get('telefone', 'Não informado')}, WhatsApp: {medico.get('whatsapp_url', 'Não informado')}, Link: {medico.get('link', 'Não informado')}" for medico in oraculo_med])}

'''


# Função para gerar o PDF
def create_pdf(messages):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for message in messages:
        role = message["role"].capitalize()
        content = message["content"]
        pdf.cell(200, 10, txt=f"{role}: {content}", ln=True)

    return pdf.output(dest='S').encode('latin1')


# Função para gerar o Excel
def create_excel(messages):
    df = pd.DataFrame(messages)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()



# Função para verificar se a pergunta está relacionada a medicamentos e saúde
def is_health_question(prompt):
    keywords = ["medicamento", "remédio", "saúde", "farmácia", "toxicologia", "farmacologia", "efeito colateral",
                "dosagem", "interação", "prescrição"]
    return any(keyword.lower() in prompt.lower() for keyword in keywords)


# Set assistant icon to Snowflake logo
icons = {"assistant": "./src/img/doutor-chat.jpg", "user": "./src/img/user-chat.jpg"}


# Replicate Credentials
with st.sidebar:
    st.markdown(
        """
        <h1 style='text-align: center;'>Doctor Med</h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
        .cover-glow {
            width: 100%;
            height: auto;
            padding: 3px;
            box-shadow: 
                0 0 5px #330000,
                0 0 10px #660000,
                0 0 15px #990000,
                0 0 20px #CC0000,
                0 0 25px #FF0000,
                0 0 30px #FF3333,
                0 0 35px #FF6666;
            position: relative;
            z-index: -1;
            border-radius: 30px;  /* Rounded corners */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    # Function to convert image to base64
    def img_to_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()


    # Load and display sidebar image with glowing effect
    img_path = "./src/img/doutor-chat.jpg"
    img_base64 = img_to_base64(img_path)
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    replicate_api = config('REPLICATE_API_TOKEN')
    st.subheader("Adjust model parameters")
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.3, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)

    st.sidebar.markdown("---")
    # Load image and convert to base64
    img_path = "./src/img/modelo-logo4.jpeg"  # Replace with the actual image path
    img_base64 = img_to_base64(img_path)

    # Display image with custom CSS class for glowing effect
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("---")

# Inicializar o modelo da Replicate
llm = Replicate(
    model="meta/meta-llama-3-70b-instruct",
    api_token=replicate_api
)

# Store LLM-generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{
        "role": "assistant", "content": 'Sou reconhecido como o Doutor Med, fui programado para demonstrar a você '
        'o poder e a velocidade em coletar informações sobre médicos.'}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=icons[message["role"]]):
        st.write(message["content"])


def clear_chat_history():
    st.session_state.messages = [{
        "role": "assistant", "content": 'Sou reconhecido como o Doutor Med, fui programado para demonstrar a você '
        'o poder e velocidade em coletar informações sobre médicos.'}]


st.sidebar.button('LIMPAR CONVERSA', on_click=clear_chat_history)
st.sidebar.caption(
    'Built by [Snowflake](https://snowflake.com/) to demonstrate [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-and-efficient-foundation-language-models-snowflake). App hosted on [Streamlit Community Cloud](https://streamlit.io/cloud). Model hosted by [Replicate](https://replicate.com/snowflake/snowflake-arctic-instruct).')
st.sidebar.caption(
    'Build your own app powered by Arctic and [enter to win](https://arctic-streamlit-hackathon.devpost.com/) $10k in prizes.')
st.sidebar.markdown("Desenvolvido por [WILLIAM EUSTÁQUIO](https://www.instagram.com/flashdigital.tech/)")

@st.cache_resource(show_spinner=False)
def get_tokenizer():
    """Get a tokenizer to make sure we're not sending too much text
    text to the Model. Eventually we will replace this with ArcticTokenizer
    """
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")


def get_num_tokens(prompt):
    """Get the number of tokens in a given prompt"""
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)


def check_safety(disable=False) -> bool:
    if disable:
        return True

    deployment = get_llamaguard_deployment()
    conversation_history = st.session_state.messages
    user_question = conversation_history[-1]  # pegar a última mensagem do usuário

    prediction = deployment.predictions.create(
        input=template)
    prediction.wait()
    output = prediction.output

    if output is not None and "unsafe" in output:
        return False
    else:
        return True




# Function for generating Snowflake Arctic response
def generate_arctic_response():
    prompt = []
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
        else:
            prompt.append("<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>")

    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    if get_num_tokens(prompt_str) >= 500:  # padrão3072
        st.error(
            "Poxa, você já atingiu seu limite de demostração, mas pode ficar tranquilo. Clique no link abaixo para "
            "pedir seu acesso.")
        st.markdown("[PEDIR ACESSO](https://sandbox.asaas.com/c/n7a2c06qy5u23vni)")
        excel_bytes = create_excel(st.session_state.messages)
        pdf_bytes = create_pdf(st.session_state.messages)
        formato_arquivo = st.selectbox("Escolha como deseja baixar sua conversa:", ["PDF", "Excel"])
        if formato_arquivo == "PDF":
            st.download_button(
                label="Baixar PDF",
                data=pdf_bytes,
                file_name="conversa.pdf",
                mime="application/pdf",
            )
        else:
            st.download_button(
                label="Baixar Excel",
                data=excel_bytes,
                file_name="conversa.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        st.stop()


    for event in replicate.stream(
            "meta/meta-llama-3-70b-instruct",
            input={
                "top_k": 0,
                "top_p": 1,
                "prompt": prompt_str,
                "temperature": 0.1,
                "system_prompt": system_prompt,
                "length_penalty": 1,
                "max_new_tokens": 500,
                "prompt_template": "<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]",
                "presence_penalty": 0,
                "log_performance_metrics": False
            },
    ):
        yield str(event)


# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="./src/img/user-chat.jpg"):
        st.write(prompt)


# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar="./src/img/doutor-chat.jpg"):
        response = generate_arctic_response()
        full_response = st.write_stream(response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)



