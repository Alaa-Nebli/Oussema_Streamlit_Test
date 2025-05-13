import streamlit as st
import requests
import time
from threading import Thread
from queue import Queue

# URL de l'agent API
AGENT_API_URL = "https://automation.neuratech-solutions.com/webhook/fea07efb-43d7-4ae1-9a6b-57a9385dfd03"

# Configuration de la page
st.set_page_config(page_title="Agent Générateur de Prompts", page_icon="💬", layout="wide")

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
if "job_started" not in st.session_state:
    st.session_state.job_started = False
if "result_queue" not in st.session_state:
    st.session_state.result_queue = Queue()
if "progress" not in st.session_state:
    st.session_state.progress = 0

# Fonction pour exécuter l'agent en arrière-plan
def run_agent_in_background(message, queue):
    try:
        response = requests.post(
            AGENT_API_URL,
            json={"message": message},
            timeout=1200  # 20 minutes timeout
        )
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list) and isinstance(data[0], dict) and "output" in data[0]:
            queue.put(("success", data[0]["output"]))
        else:
            queue.put(("error", "Réponse inattendue du serveur"))
    except Exception as e:
        queue.put(("error", f"Erreur: {str(e)}"))

# Style CSS pour améliorer l'interface
st.markdown("""
    <style>
    .stTextArea textarea {
        min-height: 150px !important;
    }
    .stProgress > div > div > div {
        background-color: #4CAF50;
    }
    .stAlert {
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Titre
st.title("🤖 Agent Générateur de Prompts (Tâches longues)")

# Section d'information
with st.expander("ℹ️ Comment utiliser cet agent"):
    st.info("""
    Cet agent peut prendre jusqu'à 10-15 minutes pour répondre à des requêtes complexes.
    - Soyez patient après avoir soumis votre requête
    - Vous pouvez quitter la page et revenir plus tard
    - Les réponses trop longues peuvent être tronquées
    """)

# Contexte Persona
with st.expander("📌 Contexte Persona (non envoyé à l'API)"):
    st.markdown(f"```markdown\n{st.session_state.prompt_system}\n```")

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Formulaire de saisie
with st.form("user_input_form"):
    user_input = st.text_area("Votre requête (soyez le plus précis possible):", 
                             value=st.session_state.user_input, 
                             height=150)
    
    submitted = st.form_submit_button("Soumettre la requête", 
                                    disabled=st.session_state.processing)

# Traitement de la soumission
if submitted and user_input.strip() and not st.session_state.processing:
    st.session_state.processing = True
    st.session_state.job_started = True
    st.session_state.user_input = user_input
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Afficher le message utilisateur
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Démarrer le thread en arrière-plan
    thread = Thread(target=run_agent_in_background, 
                   args=(user_input, st.session_state.result_queue))
    thread.start()
    
    # Afficher l'indicateur de traitement
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        
        status_placeholder.warning("🚀 Démarrage du traitement... (cela peut prendre 10-15 minutes)")
        progress_bar = progress_placeholder.progress(0)
        
        # Attendre le résultat dans la file d'attente
        while st.session_state.processing:
            time.sleep(1)
            
            # Mettre à jour la barre de progression (simulée)
            st.session_state.progress = min(st.session_state.progress + 1, 100)
            progress_bar.progress(st.session_state.progress % 100)
            
            # Vérifier si le résultat est arrivé
            if not st.session_state.result_queue.empty():
                result_type, result_content = st.session_state.result_queue.get()
                
                if result_type == "success":
                    status_placeholder.success("✅ Traitement terminé !")
                    st.session_state.messages.append({"role": "assistant", "content": result_content})
                    st.markdown(result_content)
                else:
                    status_placeholder.error(f"❌ {result_content}")
                
                st.session_state.processing = False
                st.session_state.progress = 0
                thread.join()
                break

# Bouton de réinitialisation
if st.sidebar.button("🧹 Réinitialiser la conversation", 
                    disabled=st.session_state.processing,
                    help="Efface toute l'historique de conversation"):
    st.session_state.messages = []
    st.session_state.user_input = ""
    st.session_state.processing = False
    st.session_state.job_started = False
    st.session_state.progress = 0
    st.rerun()

# Avertissement si un traitement est en cours
if st.session_state.processing:
    st.sidebar.warning("Un traitement est en cours...")
    st.balloons()  # Animation pour indiquer que le système est actif
