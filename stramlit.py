import streamlit as st
import requests

# URL de ton agent API (à modifier)
AGENT_API_URL = "https://automation.neuratech-solutions.com/webhook/fea07efb-43d7-4ae1-9a6b-57a9385dfd03"

# Configuration de la page
st.set_page_config(page_title="Agent Générateur de Prompts", page_icon="💬")

# Ton MegaPrompt comme message système (affiché mais non envoyé à l'API)
persona_prompt = """..."""  # Colle ici ton MegaPrompt complet

# Initialisation de l'état de session
if "messages" not in st.session_state:
    st.session_state.messages = []  # Historique SANS le système
if "prompt_system" not in st.session_state:
    st.session_state.prompt_system = persona_prompt  # Stocké séparément si besoin

# Fonction pour envoyer uniquement les messages utilisateur à l’API
def envoyer_au_agent(dernier_message):
    try:
        response = requests.post(AGENT_API_URL, json={"message": dernier_message})
        response.raise_for_status()
        return response.json().get("response", "Je n'ai pas compris, peux-tu reformuler ?")
    except Exception as e:
        st.error(f"Erreur API : {str(e)}")
        return "Erreur serveur. Réessaie dans un instant."

# Titre principal
st.title("🤖 Agent Générateur de Prompts")

# Affichage du MegaPrompt (optionnel)
with st.expander("📌 Contexte Persona (non envoyé à l'API)"):
    st.markdown(f"```markdown\n{st.session_state.prompt_system}\n```")

# Affichage de l’historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Saisie utilisateur
if prompt := st.chat_input("Écris ton message ici..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("✍️ Génération en cours...")

        # Appel de l’API avec SEULEMENT le dernier message utilisateur
        reponse = envoyer_au_agent(prompt)

        message_placeholder.markdown(reponse)
        st.session_state.messages.append({"role": "assistant", "content": reponse})

# Bouton pour réinitialiser
if st.sidebar.button("🧹 Réinitialiser la conversation"):
    st.session_state.messages = []
    st.rerun()
