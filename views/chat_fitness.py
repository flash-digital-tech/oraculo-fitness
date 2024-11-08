import streamlit as st
import os
from transformers import AutoTokenizer
import base64
from forms.contact import cadastrar_cliente
import replicate
from langchain.llms import Replicate
from fastapi import FastAPI, HTTPException

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from autentic.authentications import setup_authentication



# --- Verifica se o token da API está nos segredos ---
if 'REPLICATE_API_TOKEN' in st.secrets:
    replicate_api = st.secrets['REPLICATE_API_TOKEN']
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
        email = st.session_state.user_data["email"]
        whatsapp = st.session_state.user_data["whatsapp"]
        endereco = st.session_state.user_data["endereco"]

        # Construindo o corpo do e-mail
        corpo_email = f"""
        Olá {nome},

        Segue a confirmação dos dados:
        - Nome: {nome}
        - E-mail: {email}
        - WhatsApp: {whatsapp}
        - Endereço: {endereco}

        Obrigado pela confirmação!
        """

        # Enviando o e-mail
        enviar_email(email, "Confirmação de dados", corpo_email)


#######################################################################################################################

async def show_chat_fitness():
    system_prompt = f'''
    Você é o Coach Fitness. Você é um doutor em Educação física , nutrólogo e nutricionista, sua missão é conquistar 
    alunos e cadastrálos para seu projeto de 'TREINO SEMANAL' que custa somente $44,57 por semana. Primeiro você 
    usará seus conhecimentos e informações técnicas para quem não te conhece, voce conquistará as pessoas pelo 
    conteudo que oferecerá e deixará impressionados com o quanto você tem conhecimento para quem tem desejo em 
    perder e ganhar peso. Você responderá somente perguntas relacionadas ao meio fitness como: treinos, suplementação, alimentação e dicas sobre o conteúdo.
    Responda somente as perguntas sem acrescentar conteúdos ou sair fora do contexto da pergunta.
    Dê dicas e sugestões de treino, alimentação, nutrição, dietas somente se for solicitado e responda somente sobre o assunto.
    
    Percebendo o interesse do usuário faça o cadastro dele pegando primeiramente o nome e sobrenome.
    Após ele responder você pegará o WhatsApp.
    Aguarde ele responder fornecer o número do WhatsApp e pegue o endereço completo com code postal.
    
    Assim que for finalizado a coleta de dados você enviará o link para assinatura do treino semanal :
    https://buy.stripe.com/4gw3fMaTXeNZ1W06oo
    
    Assim que o sistema confirmar o pagamento o usuário receberá um link para acessar o grupo de alunos no WhatsApp.
    
    Se o cliente quiser conversar com o Vitor Coach você enviará o link do WhatsApp para entrar em contato:
    https://wa.me/+18622371396
    
    Este sistema está em modo de testes, então caso algum empresário estiver fazendo testes e quiser agendar uma reunião 
    com o programador responsável pelo desenvolvimento dessa IA que se chama Oráculo Fitness você enviará o link do 
    WhatsApp para entrar em contato: https://wa.me/+5531996011180
    
    '''

    # Set assistant icon to Snowflake logo
    icons = {"assistant": "./src/img/perfil.jpg", "user": "./src/img/usuario.jpeg"}


    # Replicate Credentials
    with st.sidebar:
        st.markdown(
            """
            <h1 style='text-align: center;'>COACH FITNESS</h1>
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
        img_path = "./src/img/perfil.jpg"
        img_base64 = img_to_base64(img_path)
        st.sidebar.markdown(
            f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("---")

        os.environ['REPLICATE_API_TOKEN'] = replicate_api

        # Load image and convert to base64
        img_path = "./src/img/perfil1.jpg"  # Replace with the actual image path
        img_base64 = img_to_base64(img_path)

        st.sidebar.markdown("---")

    # Inicializar o modelo da Replicate
    llm = Replicate(
        model="meta/meta-llama-3-70b-instruct",
        api_token=replicate_api
    )

    # Store LLM-generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content":
            'Meu nome é Vitor Coach, e é um grande prazer recebê-lo(a) em meu programa de treinamento. '
            'Sou formado em Educação Física e a minha missão é proporcionar a você uma experiência completa e transformadora, unindo o melhor das ciências do '
            'exercício e da nutrição para alcançar resultados rápidos e duradouros.'}]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.write(message["content"])


    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content":
            'Meu nome é Vitor Coach, e é um grande prazer recebê-lo(a) em meu programa de treinamento. '
            'Sou formado em Educação Física e a minha missão é proporcionar a você uma experiência completa e transformadora, unindo o melhor das ciências do '
            'exercício e da nutrição para alcançar resultados rápidos e duradouros.'}]


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

        if get_num_tokens(prompt_str) >= 3500:  # padrão3072
            if cadastro in system_prompt:
                @st.dialog("DADOS PARA PEDIDO")
                def show_contact_form():
                    cadastro


        for event in replicate.stream(
                "meta/meta-llama-3-70b-instruct",
                input={
                    "top_k": 0,
                    "top_p": 1,
                    "prompt": prompt_str,
                    "temperature": 0.1,
                    "system_prompt": system_prompt,
                    "length_penalty": 1,
                    "max_new_tokens": 3500,

                },
        ):
            yield str(event)


    # User-provided prompt
    if prompt := st.chat_input(disabled=not replicate_api):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="./src/img/usuario.jpeg"):
            st.write(prompt)


    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar="./src/img/perfil.jpg"):
            response = generate_arctic_response()
            full_response = st.write_stream(response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)



