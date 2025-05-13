import streamlit as st
import requests
import time

# URL de l'agent API
AGENT_API_URL = "https://automation.neuratech-solutions.com/webhook/fea07efb-43d7-4ae1-9a6b-57a9385dfd03"

# Configuration de la page
st.set_page_config(page_title="Agent Générateur de Prompts", page_icon="💬")

# Ton MegaPrompt
persona_prompt = """..."""  # Colle ici ton MegaPrompt complet

# État de session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "prompt_system" not in st.session_state:
    st.session_state.prompt_system = persona_prompt
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "processing" not in st.session_state:
    st.session_state.processing = False

# Fonction pour envoyer un message à l'agent avec gestion des tâches longues
def envoyer_au_agent(message):
    try:
        # First try with a reasonable timeout
        try:
            response = requests.post(
                AGENT_API_URL,
                json={"message": message},
                timeout=30  # Timeout initial de 30 secondes
            )
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and isinstance(data[0], dict) and "output" in data[0]:
                return data[0]["output"]
            return "Je n'ai pas compris la réponse du serveur."
            
        except requests.exceptions.Timeout:
            # If timeout occurs, notify user and try again with longer timeout
            st.warning("L'agent prend plus de temps que prévu. Veuillez patienter...")
            
            # Second attempt with longer timeout (10 minutes)
            response = requests.post(
                AGENT_API_URL,
                json={"message": message},
                timeout=600  # Timeout de 10 minutes pour les tâches longues
            )
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list) and isinstance(data[0], dict) and "output" in data[0]:
                return data[0]["output"]
            return "Je n'ai pas compris la réponse du serveur."
            
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return "❌ Erreur de connexion au serveur. Réessaie dans un instant."
    except Exception as e:
        st.error(f"Erreur inattendue: {str(e)}")
        return "❌ Erreur serveur. Réessaie dans un instant."

# Titre
st.title("🤖 Agent Générateur de Prompts")

# Contexte (non envoyé à l'API)
with st.expander("📌 Contexte Persona (non envoyé à l'API)"):
    st.markdown(f"```markdown\n{st.session_state.prompt_system}\n```")

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Formulaire avec champ multiligne
with st.form("user_input_form", clear_on_submit=True):
    user_input = st.text_area("Écris ton message ici…", value=st.session_state.user_input, height=100)
    submit_button = st.form_submit_button("Envoyer", disabled=st.session_state.processing)

# Traitement du message
if submit_button and user_input.strip() and not st.session_state.processing:
    st.session_state.processing = True
    st.session_state.user_input = user_input
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("✍️ Génération en cours... (cela peut prendre quelques minutes)")
        
        # Show a spinner while processing
        with st.spinner("Patientez pendant que l'agent traite votre demande..."):
            reponse = envoyer_au_agent(user_input)
            placeholder.markdown(reponse)
        
        st.session_state.messages.append({"role": "assistant", "content": reponse})
    
    st.session_state.processing = False
    st.rerun()

# Bouton reset
if st.sidebar.button("🧹 Réinitialiser la conversation", disabled=st.session_state.processing):
    st.session_state.messages = []
    st.session_state.user_input = ""
    st.rerun()
