"""
Quiz dans ta bulle 🫧
----------------------
Application Streamlit d'entraînement aux compétences sociales.
Scénarios interactifs + mini-chat bienveillant avec Mistral (Bulle).
"""

import streamlit as st
from pathlib import Path

# Configuration de la page en PREMIER - OBLIGATOIRE
st.set_page_config(
    page_title="Quiz dans ta bulle 🫧",
    page_icon="🫧", 
    layout="centered",
    initial_sidebar_state="expanded",
)

# Imports avec gestion d'erreur
@st.cache_resource
def load_modules():
    """Charge les modules avec gestion d'erreur complète"""
    try:
        from utils.scenario_loader import (
            get_random_scenario,
            get_scenarios_by_theme, 
            get_all_themes,
            get_theme_label,
            get_image_path,
            get_image_b64,
            append_generated_scenario,
        )
        from utils.mistral_client import (
            get_bulle_response,
            build_first_user_message,
            generate_scenario_with_image,
        )
        return {
            'get_random_scenario': get_random_scenario,
            'get_scenarios_by_theme': get_scenarios_by_theme,
            'get_all_themes': get_all_themes,
            'get_theme_label': get_theme_label,
            'get_image_path': get_image_path,
            'get_image_b64': get_image_b64,
            'append_generated_scenario': append_generated_scenario,
            'get_bulle_response': get_bulle_response,
            'build_first_user_message': build_first_user_message,
            'generate_scenario_with_image': generate_scenario_with_image,
        }
    except Exception as e:
        st.error(f"❌ Erreur de chargement des modules: {e}")
        return None

# Vérification rapide des services
def check_config():
    """Vérification des clés API sans importer de modules lourds"""
    try:
        mistral_ok = bool(st.secrets.get("MISTRAL_API_KEY"))
        supabase_ok = bool(st.secrets.get("SUPABASE_URL") and st.secrets.get("SUPABASE_KEY"))
        return mistral_ok, supabase_ok
    except:
        return False, False

# État de session
def init_state():
    defaults = {
        "scenario": None,
        "phase": "quiz",
        "choix_lettre": None,
        "choix_texte": None,
        "chat_messages": [],
        "seen_ids": [],
        "theme": "Clair",
        "modules": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

# Vérification des services
mistral_ok, supabase_ok = check_config()

# Interface principale
if st.session_state.modules is None:
    st.markdown('<h1 style="text-align: center; color: #7ec8e3;">Quiz dans ta bulle 🫧</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #aaa;">Explore des situations du quotidien, à ton rythme, sans jugement.</p>', unsafe_allow_html=True)
    
    with st.spinner("🔄 Chargement des modules..."):
        st.session_state.modules = load_modules()
        if st.session_state.modules:
            st.success("✅ Application prête !")
            st.rerun()
        else:
            st.error("❌ Impossible de charger l'application")
            st.info("💡 Vérifiez que tous les fichiers utils/ sont présents")
            # On continue en mode dégradé au lieu de stopper
            st.session_state.modules = {}

# Interface normale avec modules chargés
modules = st.session_state.modules

# CSS complet
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Nunito+Sans:wght@400;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'Nunito Sans', sans-serif;
  }

  h1, h2, h3 {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
  }

  .scenario-card {
    background: linear-gradient(135deg, #f0f7ff 0%, #fef9f0 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    border-left: 5px solid #7ec8e3;
    box-shadow: 0 4px 12px rgba(126, 200, 227, 0.15);
  }

  .chat-bulle {
    background: linear-gradient(135deg, #f8fdff, #f0f7ff);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #7ec8e3;
    font-size: 0.95rem;
    line-height: 1.6;
  }

  .chat-user {
    background: linear-gradient(135deg, #fff8f0, #fef9f0);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    border-right: 4px solid #ffca28;
    font-size: 0.95rem;
    line-height: 1.6;
  }

  .chat-label {
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
    color: #666;
  }

  .chosen-answer {
    background: linear-gradient(135deg, #f0fff4, #f8fdff);
    border-radius: 12px;
    padding: 0.75rem 1.1rem;
    margin: 1rem 0;
    border-left: 4px solid #ffca28;
    font-style: italic;
    font-size: 0.95rem;
  }

  .main-title {
    text-align: center;
    font-family: 'Nunito', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #7ec8e3, #b39ddb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem !important;
  }
</style>
""", unsafe_allow_html=True)

# Interface principale
st.markdown('<h1 class="main-title">Quiz dans ta bulle 🫧</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #aaa; font-size: 1.6rem; margin-bottom: 2rem;">Explore des situations du quotidien</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Paramètres")
    
    # Affichage du statut
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🤖 Mistral", "✅" if mistral_ok else "❌")
    with col2:
        st.metric("💾 Supabase", "✅" if supabase_ok else "❌")
    
    # Thème
    st.session_state.theme = st.selectbox(
        "🎨 Thème", 
        ["Clair", "Sombre"],
        index=0 if st.session_state.theme == "Clair" else 1
    )
    
    # Génération de scénarios (si Mistral OK)
    if mistral_ok and modules and 'generate_scenario_with_image' in modules:
        st.markdown("---")
        st.markdown("### 🎯 Générer un scénario")
        
        theme_custom = st.text_input("Thème personnalisé", placeholder="ex: Transport")
        if st.button("🚀 Générer", use_container_width=True):
            if theme_custom.strip():
                with st.spinner("Génération en cours..."):
                    try:
                        new_scenario = modules['generate_scenario_with_image'](theme_custom)
                        scenario_id = modules['append_generated_scenario'](new_scenario)
                        st.success(f"✅ Scénario créé ! (ID: {scenario_id})")
                    except Exception as e:
                        st.error(f"Erreur: {e}")

# Interface de données d'exemple si pas de modules
if not modules or 'get_random_scenario' not in modules:
    st.warning("⚠️ Mode dégradé - Utilisation d'un scénario d'exemple")
    
    # Scénario d'exemple codé en dur
    scenario = {
        "id": "001",
        "contexte": "Tu es dans la cour de récré. Un groupe d'élèves discute d'un nouveau jeu vidéo que tout le monde semble adorer, sauf toi qui ne l'as jamais essayé.",
        "question": "Comment réagis-tu ?",
        "options": {
            "A": "Je fais semblant de connaître le jeu pour m'intégrer",
            "B": "J'avoue que je ne connais pas et je demande qu'ils m'expliquent",
            "C": "Je change de sujet vers quelque chose que je maîtrise mieux",
            "D": "Je m'éloigne discrètement pour éviter la situation"
        },
        "commentaire": "Chaque réaction est compréhensible et révèle différentes stratégies sociales. L'important est de rester authentique tout en s'ouvrant aux autres.",
        "theme": "ecole"
    }
else:
    # Interface normale avec modules chargés
    if st.session_state.scenario is None:
        st.session_state.scenario = modules['get_random_scenario'](st.session_state.seen_ids)
        st.session_state.seen_ids.append(st.session_state.scenario["id"])
        st.session_state.phase = "quiz"
        st.session_state.chat_messages = []

    scenario = st.session_state.scenario

# Affichage du scénario
if scenario:
    st.markdown(f"""
    <div class="scenario-card">
        <h3>📖 Scénario</h3>
        <p><strong>{scenario['contexte']}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Gestion des images
    image_shown = False
    if modules and 'get_image_path' in modules:
        image_path = modules['get_image_path'](scenario["id"])
        if image_path:
            st.image(str(image_path), use_column_width=True)
            image_shown = True
    
    if not image_shown and scenario.get('image_b64'):
        try:
            import base64
            image_data = base64.b64decode(scenario['image_b64'])
            st.image(image_data, use_column_width=True)
        except:
            pass
    
    # Question
    st.markdown("#### " + scenario['question'])
    
    # Phase Quiz
    if st.session_state.phase == "quiz":
        for letter, option in scenario['options'].items():
            if st.button(f"**{letter})** {option}", key=f"opt_{letter}", use_container_width=True):
                st.session_state.choix_lettre = letter
                st.session_state.choix_texte = option
                st.session_state.phase = "chat" if mistral_ok else "result"
                st.rerun()
    
    # Phase Résultat simple (si Mistral pas configuré)
    elif st.session_state.phase == "result":
        st.markdown(f"""
        <div class="chosen-answer">
            <strong>Votre choix :</strong> {st.session_state.choix_lettre}) {st.session_state.choix_texte}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="chat-bulle">
            <div class="chat-label">🫧 Bulle</div>
            {scenario['commentaire']}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Nouveau scénario", type="primary"):
            st.session_state.scenario = None
            st.rerun()
    
    # Phase Chat avec Bulle
    elif st.session_state.phase == "chat" and mistral_ok:
        st.markdown(f"""
        <div class="chosen-answer">
            <strong>Votre choix :</strong> {st.session_state.choix_lettre}) {st.session_state.choix_texte}
        </div>
        """, unsafe_allow_html=True)
        
        # Initialisation du chat
        if not st.session_state.chat_messages:
            with st.spinner("Bulle réfléchit... 🫧"):
                try:
                    if modules and 'build_first_user_message' in modules:
                        first_message = modules['build_first_user_message'](
                            scenario['contexte'],
                            st.session_state.choix_lettre, 
                            st.session_state.choix_texte
                        )
                        bulle_response = modules['get_bulle_response']([{"role": "user", "content": first_message}])
                        st.session_state.chat_messages = [
                            {"role": "user", "content": first_message},
                            {"role": "assistant", "content": bulle_response}
                        ]
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur de chat: {e}")
                    # Fallback
                    st.markdown(f"""
                    <div class="chat-bulle">
                        <div class="chat-label">🫧 Bulle (mode hors ligne)</div>
                        {scenario['commentaire']}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Affichage du chat
        if st.session_state.chat_messages:
            st.markdown("#### 💬 Conversation avec Bulle")
            
            for i, msg in enumerate(st.session_state.chat_messages):
                if msg["role"] == "assistant":
                    st.markdown(f"""
                    <div class="chat-bulle">
                        <div class="chat-label">🫧 Bulle</div>
                        {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                elif msg["role"] == "user" and i > 0:
                    st.markdown(f"""
                    <div class="chat-user">
                        <div class="chat-label" style="text-align: right;">Vous</div>
                        {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Input utilisateur
        user_input = st.chat_input("Écrivez à Bulle...")
        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            with st.spinner("Bulle répond... 🫧"):
                try:
                    if modules and 'get_bulle_response' in modules:
                        response = modules['get_bulle_response'](st.session_state.chat_messages)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response})
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
                    st.session_state.chat_messages.pop()
        
        # Boutons de navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Nouveau scénario", use_container_width=True):
                st.session_state.scenario = None
                st.rerun()
        with col2:
            if st.button("🏠 Retour aux choix", use_container_width=True):
                st.session_state.phase = "quiz" 
                st.session_state.choix_lettre = None
                st.session_state.choix_texte = None
                st.session_state.chat_messages = []
                st.rerun()

# Footer
st.markdown("---")
st.markdown('<p style="text-align: center; color: #ccc; font-size: 0.8rem;">Quiz dans ta bulle — Entraînement bienveillant aux situations sociales</p>', unsafe_allow_html=True)