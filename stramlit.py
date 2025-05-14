import streamlit as st
import requests
import time
import uuid
from threading import Thread
from queue import Queue

# Backend API
AGENT_API_URL = "https://automation.neuratech-solutions.com/webhook/fea07efb-43d7-4ae1-9a6b-57a9385dfd03"

# Page setup
st.set_page_config(page_title="Agent Générateur de Persona", page_icon="💬", layout="wide")

# Initialize session state safely
defaults = {
    "session_id": str(uuid.uuid4()),
    "messages": [],
    "prompt_system": "...",  # Replace with your full prompt if needed
    "user_input": "",
    "processing": False,
    "result_queue": Queue(),
    "progress": 0,
}
for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Run backend agent
def run_agent(message, queue):
    try:
        response = requests.post(
            AGENT_API_URL,
            json={
                "message": message,
                "session_id": st.session_state.session_id,
            },
            timeout=1200  # 20 minutes
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and isinstance(data[0], dict) and "output" in data[0]:
            text = data[0]["output"].get("text", "⚠️ Texte manquant dans la réponse.")
            queue.put(("success", text))
        else:
            queue.put(("error", "Réponse inattendue du serveur."))
    except Exception as e:
        queue.put(("error", f"Erreur: {str(e)}"))

# Custom CSS for fixed input at bottom
st.markdown("""
    <style>
    .stTextArea textarea { min-height: 150px !important; }
    .stProgress > div > div > div { background-color: #4CAF50; }
    .block-container {
        display: flex;
        flex-direction: column;
        height: 95vh;
    }
    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding-bottom: 1rem;
    }
    .input-form {
        position: sticky;
        bottom: 0;
        background-color: white;
        padding-top: 0.5rem;
        border-top: 1px solid #eee;
    }
    </style>
""", unsafe_allow_html=True)

# Main container
with st.container():
    st.title("🎯 Agent IA – Générateur de Persona")

    # Chat messages (top area)
    with st.container():
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Input form (fixed at bottom)
    with st.form("persona_form", clear_on_submit=False):
        user_input = st.text_area("Votre requête :", value=st.session_state.user_input, height=150)
        submitted = st.form_submit_button("🔍 Générer", disabled=st.session_state.processing)

    # Form handling
    if submitted and user_input.strip() and not st.session_state.processing:
        st.session_state.processing = True
        st.session_state.user_input = user_input
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        thread = Thread(target=run_agent, args=(user_input, st.session_state.result_queue))
        thread.start()

        with st.chat_message("assistant"):
            status = st.empty()
            progress = st.progress(0)
            status.warning("🕒 Traitement en cours... Merci de patienter.")
            count = 0

            while st.session_state.processing:
                time.sleep(1)
                count += 1
                st.session_state.progress = (count * 2) % 100
                progress.progress(st.session_state.progress)

                if not st.session_state.result_queue.empty():
                    result_type, result_content = st.session_state.result_queue.get()
                    if result_type == "success":
                        status.success("✅ Persona généré avec succès !")
                        st.markdown(result_content)
                        st.session_state.messages.append({"role": "assistant", "content": result_content})
                    else:
                        status.error(f"❌ {result_content}")

                    st.session_state.processing = False
                    thread.join()
                    break

# Reset conversation from sidebar
st.sidebar.header("🧰")
if st.sidebar.button("🔄 Réinitialiser", disabled=st.session_state.processing):
    for key in ["messages", "user_input", "progress", "processing"]:
        st.session_state[key] = [] if isinstance(st.session_state[key], list) else False
    st.r
