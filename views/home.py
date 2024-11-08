import streamlit as st
from streamlit_lottie import st_lottie
import requests
import json


async def showHome():

    # --- HERO SECTION ---
    col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
    with col1:
        st.image("./src/img/perfil1.jpg", width=230)

    with col2:
        # Função para carregar animação Lottie
        def load_lottie_animation(url):
            try:
                response = requests.get(url)
                response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx
                return response.json()
            except requests.exceptions.RequestException as e:
                st.error(f"Erro ao carregar a animação: {e}")
                return None  # Retorna None se ocorrer um erro

        def load_lottie_local(filepath):
            with open(filepath) as f:
                return json.load(f)
        lottie_animation = load_lottie_local("src/animations/animation_home.json")
        st_lottie(lottie_animation, speed=1, width=400, height=400, key="animation_home")

        st.title("CHEF MANTIQUEIRA!", anchor=False)
        st.write(
            "Tecnologia de alto nível para atendimento e venda de carne online."
        )

        if st.button("✉️FAZER LOGIN"):
            pass

    # --- EXPERIENCE & QUALIFICATIONS ---
    st.write("\n")
    st.subheader("Vantagens & Benefícios", anchor=False)
    st.write(
        """
        * Atendimento Instantâneo: O agente de IA pode fornecer respostas imediatas a perguntas dos clientes, melhorando a experiência de compra.
        * Recomendações Personalizadas: A IA pode analisar preferências dos clientes e sugerir produtos, aumentando as chances de vendas adicionais.
        * Gestão de Pedidos Eficiente: O sistema pode automatizar o processo de recebimento e acompanhamento de pedidos, reduzindo erros e agilizando o atendimento.
        * Análise de Feedback: O agente pode coletar e analisar feedback dos clientes, permitindo melhorias contínuas no serviço e nas ofertas.
        * Promoções e Ofertas: A IA pode identificar oportunidades para promoções personalizadas, incentivando compras e fidelizando clientes.
        """
    )

    # --- SKILLS ---
    st.write("\n")
    st.subheader("ESCALA/CRESCIMENTO", anchor=False)
    st.write(
        """
    1. Atendimento em Grande Escala: O agente de IA pode atender simultaneamente a múltiplos clientes, eliminando limitações de capacidade humana e permitindo que a empresa cresça sem a necessidade de aumentar proporcionalmente a equipe.
    2. Redução de Custos Operacionais: Com a automação de tarefas repetitivas, as empresas podem reduzir custos com pessoal, permitindo alocar recursos para outras áreas essenciais do negócio.
    3. Adaptação a Picos de Demanda: O sistema pode facilmente lidar com aumentos repentinos na demanda, como durante promoções ou datas comemorativas, garantindo que o atendimento ao cliente nunca seja comprometido.
    4. Expansão Geográfica: Com a IA atuando em canais digitais, as empresas podem alcançar novos mercados e clientes sem a necessidade de presença física, facilitando a expansão.
    5. Análise de Dados em Tempo Real: O agente de IA pode processar e analisar grandes volumes de dados sobre interações com clientes, permitindo que as empresas ajustem suas estratégias rapidamente para atender a novas demandas e tendências.
        """
    )

