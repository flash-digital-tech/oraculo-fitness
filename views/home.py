import streamlit as st
from streamlit_lottie import st_lottie
import requests
import json
from forms.contact import cadastrar_cliente  # Importando a função de cadastro

async def showHome():
    # Adicionando Font Awesome para ícones e a nova fonte
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700&display=swap');
        .title {
            text-align: center;
            font-size: 50px;
            font-family: 'Poppins', sans-serif;
        }
        .highlight {
            color: #6A0DAD; /* Lilás escuro */
        }
        .subheader {
            text-align: center;
            font-size: 30px;
            font-family: 'Poppins', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Título da página
    st.markdown(
        f"<h1 class='title'>Transforme Seu Corpo em 12 Semanas com <span class='highlight'>Coach Vitor</span></h1>",
        unsafe_allow_html=True
    )

    # Apresentação do Coach Vitor
    st.write("Olá! Meu nome é Vitor, e sou um personal trainer dedicado a ajudar pessoas a alcançar uma transformação completa de corpo e mente. Com uma abordagem prática e estratégica, desenvolvi o programa “Transforme Seu Corpo em 12 Semanas” para proporcionar mudanças reais e duradouras na sua saúde e forma física.")

    # Exibindo a imagem do Coach Vitor
    st.image("./src/img/perfil-home.png", width=230)

    # --- O QUE VOCÊ RECEBERÁ COM O PROGRAMA ---
    st.subheader("O Que Você Receberá com o Programa", anchor=False)
    st.write(
        """
        * **Treinos Personalizados:** Cada treino é desenhado para se ajustar às suas metas e necessidades, garantindo que você maximize seus resultados e aprenda as técnicas corretas para cada exercício.
        * **Ebooks Exclusivos:** Além de um ebook completo de nutrição, você terá acesso a uma série de ebooks cobrindo temas importantes de saúde, treino e mentalidade, ajudando você a obter o conhecimento necessário para sustentar suas conquistas a longo prazo.
        * **Suporte Direto e Exclusivo:** Estarei ao seu lado em cada passo dessa jornada. Com o suporte direto, você terá orientação para tirar dúvidas, manter a motivação e aprender mais sobre cada etapa do processo.
        * **Materiais Educativos:** Você terá acesso a conteúdos educativos sobre treinamento, nutrição e saúde, desenvolvidos para empoderar você com conhecimento e permitir que mantenha os resultados mesmo após o programa.
        * **Bônus Exclusivos para Inscrições Imediatas:** Esta é uma oportunidade exclusiva, e as vagas são limitadas. Inscreva-se agora para garantir o acesso aos bônus que foram criados especialmente para você e que vão acelerar seus resultados. Não perca sua chance de fazer parte deste grupo seleto – as vagas são poucas e preenchidas rapidamente.
        """
    )

    # --- CHAMADA À AÇÃO ---
    st.write("\n")
    st.markdown(
        f"<h2 class='subheader'>Pronto para transformar seu corpo e sua mente?</h2>",
        unsafe_allow_html=True
    )
    st.write("As vagas são limitadas. Vamos começar essa jornada juntos!")

    # --- BOTÃO DE INSCRIÇÃO ---
    if st.button("✉️ INSCREVA-SE AGORA"):
        # Chama a função de cadastro que contém o modal
        nome, whatsapp, endereco = cadastrar_cliente()  # Modifique a função para retornar os valores

        # Verifica se os campos foram preenchidos
        if nome and whatsapp and endereco:
            # Se todos os campos estiverem preenchidos, exibe a mensagem de sucesso
            st.success("Cadastro feito com sucesso!!!")
        else:
            # Se algum campo estiver vazio, exibe uma mensagem de erro
            st.error("Por favor, preencha todos os campos antes de confirmar o cadastro.")


