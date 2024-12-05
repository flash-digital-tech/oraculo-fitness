import streamlit as st
from streamlit_authenticator import Authenticate
import yaml
import asyncio
from views.home import showHome
from views.chat_fitness import show_chat_fitness
from views.chat_fitness_demo import showChatDemo
from views.financeiro import show_financeiro
from views.cliente_criar import show_create_customer
from views.link_pagamento import show_pagamento_links
from views.webhooks import show_webhooks
from views.assinatura import show_assinaturas
from views.criar_parceiro import showSubconta
from views.split import show_split_pagamento
import base64


# --- LOAD CONFIGURATION ---
try:
    with open("config.yaml") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    st.error("Arquivo de configuração não encontrado.")
    st.stop()
except yaml.YAMLError as e:
    st.error(f"Erro ao carregar o arquivo de configuração: {e}")
    st.stop()


# --- AUTHENTICATION SETUP ---
credentials = {
    'usernames': {user['username']: {
        'name': user['name'],
        'password': user['password'],
        'email': user['email'],
        'role': user['role'],
        'whatsapp': user.get('whatsapp', ''),
        'endereco': user.get('endereco', ''),
        'cep': user.get('cep', ''),
        'bairro': user.get('bairro', ''),
        'cidade': user.get('cidade', ''),
        'cpf_cnpj': user.get('cpf_cnpj', ''),
        'created_at': user.get('created_at', '')
    } for user in config['credentials']['users']}
}

authenticator = Authenticate(
    credentials=credentials,
    cookie_name=config['cookie']['name'],
    key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)


# --- PAGE SETUP ---
authenticator.login()

if 'authentication_status' in st.session_state and st.session_state['authentication_status']:
    user_email = next(user['email'] for user in config['credentials']['users'] if user['username'] == st.session_state['username'])
    authenticator.logout('SAIR', 'sidebar')
    st.sidebar.markdown(
            """
            <h1 style='text-align: center;'>COACH FITNESS</h1>
            """,
            unsafe_allow_html=True
        )

    st.sidebar.markdown(
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
    img_path = "./src/img/logo1.jpg"
    img_base64 = img_to_base64(img_path)
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.title("MENU")
    st.sidebar.markdown("---")
    st.sidebar.write(f'Bem Vindo(a) *{st.session_state["name"]}*')

    if 'username' in st.session_state:
        user_role = next((user['role'] for user in config['credentials']['users'] if user['username'] == st.session_state['username']), None)
        if user_role is None:
            st.error("Usuário não encontrado.")
            st.stop()
    else:
        st.error("Usuário não está autenticado.")
        st.stop()

    permissao_usuario = {
        "admin": ["Apresentação", "VITOR COACH", "Chat Demo", "Criar Cliente","Criar Parceiro", "Financeiro", "Link de Pagamento", \
                  "Webhook","Assinaturas","Split de Pagamentos",],
        "parceiro": ["Apresentação", "VITOR COACH", "Chat Demo",, "Criar Cliente","Assinaturas", "Link de Pagamento"],
        "cliente": ["Chat Demo", "Apresentação"],
    }

    paginas_permitidas = permissao_usuario.get(user_role, [])

    pages = {
        "Apresentação": showHome,
        "VITOR COACH": show_chat_fitness,
        "Chat Demo": showChatDemo,
        "Criar Cliente": show_create_customer,
        "Criar Parceiro": showSubconta,
        "Assinaturas": show_assinaturas,
        "Financeiro": show_financeiro,
        "Split de Pagamentos": show_split_pagamento,
        "Link de Pagamento": show_pagamento_links,
        "Webhook": show_webhooks,
    }

    allowed_pages = {key: pages[key] for key in paginas_permitidas if key in pages}

    navigation_structure = {
        "MENU": list(allowed_pages.keys())
    }

    selected_page = st.sidebar.radio("PÁGINAS:", navigation_structure["MENU"])

    # Executando a função da página selecionada
    async def main():
        if selected_page in allowed_pages:
            await allowed_pages[selected_page]()  # Chama a função correspondente

    if __name__ == '__main__':
        asyncio.run(main())

elif st.session_state["authentication_status"] is False:
    st.error("Usuário/Senha inválido")
elif st.session_state["authentication_status"] is None:
    st.warning("Por Favor, utilize seu usuário e senha!")
