import openai
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import openai
import os

load_dotenv()
openai.api_key =st.secrets["GPT4"]


def lire_prompt():
    with open("prompt.txt", "r") as file:
        return file.read()

# Configuration de la page
st.set_page_config(page_title="Adaptech", page_icon="wheelchair")
st.markdown("<h1 style='text-align: center;'>Adaptech</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Vous assiste dans la recherche d'aides techniques</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Cet outil doit faire un diagnostic, puis vous proposer une première approche avec des recommandations.<br> Enfin, il doit vous proposer 3 modèles différents, idéalement dans un tableau. <br>S'il ne va pas jusqu'au bout n'hésitez pas à le relancer en mettant <i><b>continue</b></i> dans sa boite de dialogue</p>", unsafe_allow_html=True)


# Clé API OpenAI
#openai.api_key = "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"

# Initialisation des variables de session
prompt = lire_prompt()
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "system", "content": prompt}]
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0
if 'cost' not in st.session_state:
    st.session_state['cost'] = []

# Toujours utiliser le modèle GPT-4
model = "gpt-4"

# Placeholder pour le coût total
counter_placeholder = st.empty()
counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

# Fonction pour générer une réponse
def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    with st.spinner('Je recherche...'):
        completion = openai.ChatCompletion.create(
            model=model,
            messages=st.session_state['messages']
        )
        response = completion.choices[0].message.content
        st.session_state['messages'].append({"role": "assistant", "content": response})

        total_tokens = completion.usage.total_tokens
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000
        return response, total_tokens, prompt_tokens, completion_tokens, cost

# Container pour l'historique des messages
response_container = st.container()

# Gestion de la saisie utilisateur
with st.form(key='my_form', clear_on_submit=True):
    user_input = st.text_area("You:", key='input', height=100)
    submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens, cost = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['total_tokens'].append(total_tokens)
        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

# Affichage de l'historique des messages
if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
            st.write(f"Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")

# Bouton "Continuer" (optionnel)
if len(st.session_state['generated']) > 5:
    if st.button("Continuer"):
        st.write("La conversation continue...")
        counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
