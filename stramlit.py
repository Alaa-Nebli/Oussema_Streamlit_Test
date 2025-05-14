import streamlit as st
import requests
import uuid
from datetime import datetime

# Backend API URL
AGENT_API_URL = "https://automation.neuratech-solutions.com/webhook/fea07efb-43d7-4ae1-9a6b-57a9385dfd03"

# Set up Streamlit page
st.set_page_config(page_title="🤖 Chat IA - Neuratech", page_icon="💬", layout="centered")

st.markdown(
    """
    <style>
    .stTextInput > div > div > input {
        padding: 1rem;
        border-radius: 0.5rem;
        font-size: 1.1rem;
    }
    .stButton button {
        border-radius: 0.5rem;
        padding: 0.5rem 1.5rem;
        font-size: 1rem;
        background-color: #4A90E2;
        color: white;
        border: none;
    }
    .chat-bubble {
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        max-width: 80%;
        word-wrap: break-word;
    }
    .user {
        background-color: #DCF8C6;
        align-self: flex-end;
    }
    .agent {
        background-color: #F1F0F0;
        align-self: flex-start;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Title
st.title("💬 Chat IA avec Neuratech")

# Chat container
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        bubble_class = "user" if role == "user" else "agent"
        st.markdown(f'<div class="chat-container"><div class="chat-bubble {bubble_class}">{content}</div></div>', unsafe_allow_html=True)

# Input field
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Votre message :", "")
    submitted = st.form_submit_button("Envoyer")

# Send message to backend
def send_message_to_backend(message, session_id):
    try:
        response = requests.post(
            AGENT_API_URL,
            json={"message": message, "session_id": session_id},
            timeout=1200  # 20 minutes
        )
        response.raise_for_status()
        return response.json().get("output", "❌ Erreur : réponse inattendue.")
    except Exception as e:
        return f"❌ Une erreur s'est produite : {e}"

# On form submit
if submitted and user_input.strip() != "":
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Send to backend
    with st.spinner("L'agent réfléchit..."):
        bot_reply = send_message_to_backend(user_input, st.session_state.session_id)

    # Append bot reply
    st.session_state.messages.append({"role": "agent", "content": bot_reply})

    # Refresh page to display
    st.rerun()
