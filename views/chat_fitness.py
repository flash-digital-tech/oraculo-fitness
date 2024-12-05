import asyncio

import streamlit as st
from transformers import AutoTokenizer
import base64
import pandas as pd
import io
from fastapi import FastAPI
import stripe
from util import carregar_arquivos
import os
import glob
from forms.contact import cadastrar_cliente, agendar_reuniao 

import replicate
from langchain.llms import Replicate

from key_config import API_KEY_STRIPE, URL_BASE
from decouple import config


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


#######################################################################################################################

def show_chat_fitness():

    if "image" not in st.session_state:
        st.session_state.image = None
    
    def ler_arquivos_txt(pasta):
        """
        Lê todos os arquivos .txt na pasta especificada e retorna uma lista com o conteúdo de cada arquivo.

        Args:
            pasta (str): O caminho da pasta onde os arquivos .txt estão localizados.

        Returns:
            list: Uma lista contendo o conteúdo de cada arquivo .txt.
        """
        conteudos = []  # Lista para armazenar o conteúdo dos arquivos

        # Cria o caminho para buscar arquivos .txt na pasta especificada
        caminho_arquivos = os.path.join(pasta, '*.txt')

        # Usa glob para encontrar todos os arquivos .txt na pasta
        arquivos_txt = glob.glob(caminho_arquivos)

        # Lê o conteúdo de cada arquivo .txt encontrado
        for arquivo in arquivos_txt:
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()  # Lê o conteúdo do arquivo
                conteudos.append(conteudo)  # Adiciona o conteúdo à lista

        return conteudos  # Retorna a lista de conteúdos

    # Exemplo de uso da função
    pasta_conhecimento = './conhecimento'  # Caminho da pasta onde os arquivos .txt estão localizados
    conteudos_txt = ler_arquivos_txt(pasta_conhecimento)

    is_in_registration = False
    is_in_scheduling = False


    # Função para verificar se a pergunta está relacionada a cadastro
    def is_health_question(prompt):
        keywords = ["cadastrar", "inscrição", "quero me cadastrar", "gostaria de me registrar",
                    "desejo me cadastrar", "quero fazer o cadastro", "quero me registrar", "quero me increver",
                    "desejo me registrar", "desejo me inscrever","eu quero me cadastrar", "eu desejo me cadastrar",
                    "eu desejo me registrar", "eu desejo me inscrever", "eu quero me registrar", "eu desejo me registrar",
                    "eu quero me inscrever"]
        return any(keyword.lower() in prompt.lower() for keyword in keywords)

    #Função que analisa desejo de agendar uma reunião
    def is_schedule_meeting_question(prompt):
        keywords = [
            "agendar reunião", "quero agendar uma reunião", "gostaria de agendar uma reunião",
            "desejo agendar uma reunião", "quero marcar uma reunião", "gostaria de marcar uma reunião",
            "desejo marcar uma reunião", "posso agendar uma reunião", "posso marcar uma reunião",
            "Eu gostaria de agendar uma reuniao", "eu quero agendar", "eu quero agendar uma reunião,",
            "quero reunião"
        ]
        return any(keyword.lower() in prompt.lower() for keyword in keywords)

    # Atualizando o system_prompt
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
    
    Responda as perguntas e tire dúvidas de acordo com a FAC abaixo:
    
    ### What does the “Transforme Seu Corpo em 12 Semanas” program include?
    It includes all my Ebooks covering training, eating reeducation, injury prevention, mental support, and more.
    
    ---
    
    ### How is this program different from other fitness programs?
    I provide access to extensive knowledge, helping people change their bodies, minds, and lives with insights they won't find elsewhere.
    
    ---
    
    ### Will the program be customized to my specific goals?
    Yes, our programs are tailored to meet clients' needs and various approaches to achieve your dream physique.
    
    ---
    
    ### What type of workouts will I be doing in the 12-week program?
    The program focuses mainly on strength training and high-intensity cardio to optimize results within a short workout timeframe.
    
    ---
    
    ### How often will I need to work out each week?
    The program is designed for 3 days a week, with 2 extra high-intensity circuit workouts lasting about 20 minutes each.
    
    ---
    
    ### Do I need gym access for this program, or can it be done at home?
    Access to a gym is advised, as the program primarily focuses on strength training requiring equipment.
    
    ---
    
    ### Can the program be tailored to work around my current injuries?
    Yes, we recommend contacting Coach Vitor for a physical evaluation and personalized training around your needs.
    
    ---
    
    ### Will I have to follow a strict diet plan?
    I advocate for eating reeducation rather than strict diets, focusing on sustainable lifestyle changes instead.
    
    ---
    
    ### Do you offer any flexibility with the exercises in the program?
    Following the exercises as designed is crucial for optimal results, unless health concerns arise, in which case contact Coach Vitor.
    
    ---
    
    ### How long are the workouts in each session?
    Most sessions take around 40-50 minutes, depending on your efficiency.
    
    ---
    
    ### What is a physical evaluation, and what does it entail?
    It's a comprehensive assessment that helps create a tailored workout plan based on your needs and limitations.
    
    ---
    
    ### Will I get help with nutrition alongside the workout plan?
    We teach you about nutrition so you can create your own flexible meals without following a strict diet.
    
    ---
    
    ### What if I don’t see results in 12 weeks?
    We offer a 30-day money-back guarantee if you aren't satisfied with your results.
    
    ---
    
    ### Can I cancel the program if I feel it’s not right for me?
    Yes, we have a 30-day money-back guarantee if you follow the plan and are not satisfied.
    
    ---
    
    ### Is the program suitable for beginners, or is it more advanced?
    The program welcomes everyone, placing you in a group with similar fitness levels for safe progression.
    
    ---
    
    ### Are there rest days in the program?
    Yes, there are 4 rest days each week, plus 2 optional high-intensity workouts.
    
    ---
    
    ### Will there be cardio exercises included?
    Yes, the extra workouts focus on high-intensity cardio to accelerate your results.
    
    ---
    
    ### Can the program help me gain muscle and lose fat at the same time?
    Yes, but it's recommended to focus on one goal at a time for the best results.
    
    ---
    
    ### Is there a one-on-one aspect to the program, or is it fully self-guided?
    You can reach out to Coach Vitor via WhatsApp for additional guidance.
    
    ---
    
    ### What kind of equipment will I need to complete the program?
    Basic gym equipment like dumbbells, barbells, and cables is required.
    
    ---
    
    ### How do you track progress throughout the 12 weeks?
    We recommend taking before and bi-weekly progress photos to compare changes.
    
    ---
    
    ### What’s the next step after finishing the 12-week program?
    We evaluate your progress and create a plan for your next goals, whether it's weight loss or muscle gain.
    
    ---
    
    ### Do you offer any add-ons or follow-up programs after the 12 weeks?
    Yes, we renew your training every 12 weeks to ensure continued progress.
    
    ---
    
    ### Do I need any supplements to get the best results?
    Supplements are optional; we provide an ebook detailing their benefits.
    
    ---
    
    ### What types of bonuses come with the program?
    You receive extra training sessions and access to all my ebooks at no additional cost.
    
    ---
    
    # Personal Trainer and Coaching Questions
    
    ---
    
    ### What makes you qualified to train clients?
    I have years of experience and certifications from ISSA, specializing in injury prevention and athletic science.
    
    ---
    
    ### How long have you been a personal trainer?
    I’ve been certified for a year, but I've been training people for over 4 years.
    
    ---
    
    ### What sets you apart from other trainers?
    I prioritize safety and a goal-centered approach, ensuring clients' health and well-being.
    
    ---
    
    ### Have you personally gone through weight loss or muscle building yourself?
    Yes, I overcame my own weight issues and now help others achieve their personal goals.
    
    ---
    
    ### Do you have testimonials from previous clients?
    Yes, many clients prefer to remain anonymous, but their successes speak for themselves.
    
    ---
    
    ### How do you handle clients who are new to fitness?
    I start with an acclimation period, focusing on conditioning and proper exercise form.
    
    ---
    
    ### Will I have direct access to you for questions?
    Yes, you can contact me via WhatsApp during office hours.
    
    ---
    
    ### How quickly do you respond to messages from clients?
    Response times vary depending on my schedule, but I aim to reply promptly.
    
    ---
    
    ### What kind of clients do you typically work with?
    I work with a diverse range of clients, regardless of age or fitness level.
    
    ---
    
    ### How do you stay updated with the latest training methods?
    I constantly study and take courses to refine my skills.
    
    ---
    
    ### Can you share examples of results your clients have achieved?
    For example, Lucas lost 20 pounds in nine months and gained confidence and strength.
    
    ---
    
    ### What’s your approach to injury prevention?
    I emphasize safety and have training in injury prevention techniques from a physical therapy internship.
    
    ---
    
    ### Do you work with clients of all ages?
    Yes, I believe everyone has the right to improve their health and lifestyle.
    
    ---
    
    ### How can you help me build discipline and stay motivated?
    I provide resources on nutrition and mental health, and I'm always available for support.
    
    ---
    
    # Results and Goals Questions
    
    ---
    
    ### Will I be able to see results in 12 weeks?
    You’ll see small changes in the first few weeks, leading to significant improvements by the end.
    
    ---
    
    ### Can this program help me get six-pack abs?
    Yes, depending on your body fat levels, it's possible to achieve this within the program timeframe.
    
    ---
    
    ### How quickly can I expect to see changes in my body?
    You can expect to see positive changes within 3-4 weeks.
    
    ---
    
    ### Will this program help me lose weight or gain muscle?
    Yes, it caters to both weight loss and muscle building goals.
    
    ---
    
    ### Can you help me set realistic fitness goals?
    Absolutely, we work together to establish and achieve realistic goals.
    
    ---
    
    ### What happens if I don’t reach my goals by the end of the program?
    We’ll analyze why and adjust your plan to ensure future success.
    
    ---
    
    ### How much weight can I expect to lose with this program?
    You could lose around 2lbs of body fat per week, depending on your starting point.
    
    ---
    
    ### Will my body fat percentage decrease on this program?
    Yes, our focus is on fat loss while building a strong foundation for muscle growth.
    
    ---
    
    ### Can this program help me improve flexibility and mobility?
    Yes, we provide resources to enhance flexibility and prevent injuries.
    
    ---
    
    ### How do you measure success in the program?
    Success is measured by client satisfaction and progress made throughout the program.
    
    ---
    
    # Technical and Logistical Questions
    
    ---
    
    ### Is there an app for tracking my workouts?
    All tracking is done through our WhatsApp members-only groups.
    
    ---
    
    ### How do I get started once I sign up?
    You'll be added to the group that best fits your goals.
    
    ---
    
    ### Will I have a workout calendar to follow?
    Yes, workouts are released daily in the morning.
    
    ---
    
    ### How are workouts delivered to me?
    Workouts are shared through our WhatsApp groups.
    
    ---
    
    ### What if I have questions about an exercise form?
    We provide detailed videos and texts, and you can always reach out for help.
    
    ---
    
    ### Will the program adapt if I travel or miss workouts?
    You are responsible for missed workouts, but you can always reach out for support.
    
    ---
    
    ### Can I access the program on my phone or tablet?
    Yes, you can access everything via WhatsApp.
    
    ---
    
    ### How is my progress logged and reviewed?
    You can send your starting information and pictures to create a client file for tracking.
    
    ---
    
    ### What’s the format for the eBooks included in the program?
    The eBooks are in PDF format for easy access.
    
    ---
    
    ### Will I need to provide any information before starting the program?
    Yes, we ask for personal information for reference.
    
    ---
    
    ### Are there live check-ins or just messages?
    Primarily messages, but you can schedule phone or in-person check-ins.
    
    ---
    
    ### How long do I have access to the program materials?
    You have lifetime access to the eBooks, but workout sessions are available for 24 hours.
    
    ---
    
    ### Do you offer support in case of technical issues?
    Yes, we provide assistance for any technical difficulties.
    
    ---
    
    ### Will I have access to all the eBooks immediately?
    Yes, you can access the eBooks as soon as you sign up.
    
    ---
    
    # Pricing and Guarantee Questions
    
    ---
    
    ### How much does the program cost in total?
    The total cost is $44.57 weekly, amounting to $534.84 for 12 weeks.
    
    ---
    
    ### What does the $44.57 weekly rate cover?
    It covers all eBooks, training sessions, and special gifts for early subscribers.
    
    ---
    
    ### Why is there a limited number of spots for this program?
    To ensure quality attention and support for each client.
    
    ---
    
    ### Do you offer any discounts if I pay upfront?
    No discounts are offered for upfront payments.
    
    ---
    
    ### Is there a money-back guarantee, and how does it work?
    Yes, we offer a 30-day refund policy if you’re unsatisfied with your results.
    
    ---
    
    ### How does the 30-day refund policy work?
    Contact us for a full refund if you don’t see results within the first month.
    
    ---
    
    ### Are there additional fees for personal support?
    Fees may vary based on the level of support needed, but I strive to be available for all clients.
    
    ---
    
    ### What payment methods do you accept?
    We accept card payments only.
    
    ---
    
    ### What happens if I miss a weekly payment?
    You will be removed from the group until your payment is made.
    
    ---
    
    ### Do I get to keep the materials if I don’t complete the program?
    Yes, you can keep all materials even if you don't finish the program.
    
    ---
    
    ### Why are you offering this program at a discounted rate?
    I am passionate about helping people change their lives, not just for profit.
    
    ---
    
    ### How do I secure my spot in the program before it fills up?
    Reach out via chat or WhatsApp for payment information to secure your spot!
    '''

    st.markdown(
        """
        <style>
        .highlight-creme {
            background: linear-gradient(90deg, #f5f5dc, gold);  /* Gradiente do creme para dourado */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }
        .highlight-dourado {
            background: linear-gradient(90deg, gold, #f5f5dc);  /* Gradiente do dourado para creme */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Título da página
    st.markdown(
        f"<h1 class='title'>Estude com o <span class='highlight-creme'>VITOR</span> <span class='highlight-dourado'>COACH</span></h1>",
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

    st.sidebar.markdown("---")

    # Load and display sidebar image with glowing effect
    img_path = "./src/img/perfil-home.png"
    img_base64 = img_to_base64(img_path)
    st.sidebar.markdown(
        f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
        unsafe_allow_html=True,
    )


    # Inicializar o modelo da Replicate
    llm = Replicate(
        model="meta/meta-llama-3.1-405b-instruct",
        api_token=replicate_api
    )

    # Store LLM-generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{
            "role": "assistant", "content": '🌟 Bem-vindo ao Vitor Coach! Seu coach profissional em treinamento físico.'}]

    # Dicionário de ícones
    icons = {
        "assistant": "./src/img/perfil-home.png",  # Ícone padrão do assistente
        "user": "./src/img/usuario.jpeg"           # Ícone padrão do usuário
    }
    
    # Caminho para a imagem padrão
    default_avatar_path = "./src/img/usuario.jpeg"
    
     # Exibição das mensagens
    for message in st.session_state.messages:
        if message["role"] == "user":
            # Verifica se a imagem do usuário existe
            avatar_image = st.session_state.image if "image" in st.session_state and st.session_state.image else default_avatar_path
        else:
            avatar_image = icons["assistant"]  # Ícone padrão do assistente
    
        with st.chat_message(message["role"], avatar=avatar_image):
            st.write(message["content"])


    def clear_chat_history():
        st.session_state.messages = [{
            "role": "assistant", "content": '🌟 Bem-vindo ao Vitor Coach! Seu coach profissional em treinamento físico.'}]


    st.sidebar.button('LIMPAR CONVERSA', on_click=clear_chat_history, key='limpar_conversa')

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

        if is_health_question(prompt_str):
            cadastrar_cliente()


        if is_schedule_meeting_question(prompt_str):
            agendar_reuniao()

        for event in replicate.stream(
                "meta/meta-llama-3.1-405b-instruct",
                input={
                    "top_k": 0,
                    "top_p": 1,
                    "prompt": prompt_str,
                    "temperature": 0.1,
                    "system_prompt": system_prompt,
                    "length_penalty": 1,
                    "max_new_tokens": 8000,
                },
        ):
            yield str(event)


    def get_avatar_image():
        """Retorna a imagem do usuário ou a imagem padrão se não houver imagem cadastrada."""
        if st.session_state.image is not None:
            return st.session_state.image  # Retorna a imagem cadastrada
        else:
            return default_avatar_path  # Retorna a imagem padrão
    
    # User-provided prompt
    if prompt := st.chat_input(disabled=not replicate_api):
        st.session_state.messages.append({"role": "user", "content": prompt})
    
        # Chama a função para obter a imagem correta
        avatar_image = get_avatar_image()
    
        with st.chat_message("user", avatar=avatar_image):
            st.write(prompt)
    
    # Generate a new response if last message is not from assistant
    if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar="./src/img/perfil-home.png"):
            response = generate_arctic_response()
            full_response = st.write_stream(response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
