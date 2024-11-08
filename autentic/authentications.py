import streamlit as st
from streamlit_authenticator import Authenticate
import yaml
from yaml.loader import SafeLoader

def setup_authentication():
    # --- LOAD CONFIGURATION ---
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    # --- AUTHENTICATION SETUP ---
    credentials = {
        'usernames': {user['username']: {
            'name': user['name'],
            'password': user['password'],  # Idealmente use hashes
        } for user in config['credentials']['users']}
    }

    # Instanciando o autentificador
    authenticator = Authenticate(
        credentials=credentials,
        cookie_name=config['cookie']['name'],
        key=config['cookie']['key'],
        cookie_expiry_days=config['cookie']['expiry_days']
    )

    return authenticator
