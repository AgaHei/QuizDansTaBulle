"""
Quiz dans ta bulle 🫧
----------------------
Application Streamlit d'entraînement aux compétences sociales.
Scénarios interactifs + mini-chat bienveillant avec Mistral (Bulle).
"""

import base64
import streamlit as st
from pathlib import Path

# Chargement conditionnel des variables d'environnement (local seulement)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Sur Streamlit Cloud, les secrets sont injectés automatiquement
    pass

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

# ── Configuration de la page ───────────────────────────────────────────────────

st.set_page_config(
    page_title="Quiz dans ta bulle 🫧",
    page_icon="🫧",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS personnalisé ───────────────────────────────────────────────────────────

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

  /* Carte scénario */
  .scenario-card {
    background: linear-gradient(135deg, #f0f7ff 0%, #fef9f0 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    border-left: 5px solid #7ec8e3;
    box-shadow: 0 4px 15px rgba(126,200,227,0.15);
  }

  .scenario-card p {
    font-size: 1.25rem !important;
    line-height: 1.7 !important;
    font-weight: 500 !important;
  }

  /* Badge thème */
  .theme-badge {
    display: inline-block;
    background: #7ec8e3;
    color: white;
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    margin-bottom: 1rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }

  /* Bulle de chat */
  .chat-bulle {
    background: linear-gradient(135deg, #e8f5e9, #f3e5f5);
    border-radius: 18px 18px 18px 4px;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    font-size: 0.97rem;
    line-height: 1.6;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }

  .chat-user {
    background: linear-gradient(135deg, #e3f2fd, #e8eaf6);
    border-radius: 18px 18px 4px 18px;
    padding: 0.75rem 1.25rem;
    margin: 0.5rem 0;
    font-size: 0.97rem;
    line-height: 1.6;
    text-align: right;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }

  .chat-label {
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    font-size: 0.78rem;
    color: #888;
    margin-bottom: 0.2rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  /* Réponse choisie */
  .chosen-answer {
    background: #fff8e1;
    border-radius: 12px;
    padding: 0.75rem 1.1rem;
    margin: 1rem 0;
    border-left: 4px solid #ffca28;
    font-style: italic;
    font-size: 0.95rem;
  }

  /* Titre principal */
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

  .main-subtitle {
    text-align: center;
    color: #aaa;
    font-size: 1.6rem;
    margin-bottom: 2rem;
    font-weight: 500;
  }

  /* Expander accueil */
  .welcome-block {
    background: linear-gradient(135deg, #f8f9ff, #fff8fd);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.5rem;
    border: 1px solid #e8eaf6;
  }

  .welcome-step {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
    font-size: 0.97rem;
    line-height: 1.6;
  }

  .welcome-step-icon {
    font-size: 1.2rem;
    flex-shrink: 0;
    margin-top: 0.05rem;
  }

  .confidentialite-block {
    background: #f0fdf4;
    border-radius: 12px;
    padding: 0.75rem 1.1rem;
    margin-top: 1rem;
    border-left: 3px solid #86efac;
    font-size: 0.88rem;
    color: #555;
    line-height: 1.6;
  }

  /* Masquer le label vide des text_input */
  .stTextInput > label { display: none; }

  /* Boutons Streamlit — arrondi */
  .stButton > button {
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
  }

  /* Questions et boutons de réponse */
  .question-section h4 {
    font-size: 1.4rem !important;
    margin-bottom: 1.5rem !important;
  }
</style>
""", unsafe_allow_html=True)

# ── État de session ────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "scenario": None,
        "phase": "quiz",
        "choix_lettre": None,
        "choix_texte": None,
        "chat_messages": [],
        "seen_ids": [],
        "loading_chat": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🫧 Quiz dans ta bulle")
    st.markdown("---")

    st.markdown("### 🎯 Choisir un thème")
    themes = ["Aléatoire"] + [get_theme_label(t) for t in get_all_themes()]
    theme_choice = st.selectbox("Thème", themes, label_visibility="collapsed")

    st.markdown("---")

    if st.button("✨ Nouveau scénario", use_container_width=True, type="primary"):
        if theme_choice == "Aléatoire":
            scenario = get_random_scenario(exclude_ids=st.session_state.seen_ids)
        else:
            theme_key = next(
                (k for k, v in {
                    "ecole":           "🏫 École & formation",
                    "amitie":          "👫 Amitié & groupe",
                    "famille":         "👨‍👩‍👧 Famille",
                    "quotidien":       "🏙️ Vie quotidienne",
                    "reseaux_sociaux": "📱 Réseaux sociaux",
                    "pro":             "💼 Vie pro & stages",
                    "relations":       "❤️ Relations",
                }.items() if v == theme_choice),
                None
            )
            pool = get_scenarios_by_theme(theme_key) if theme_key else []
            seen_in_theme = [s for s in st.session_state.seen_ids
                             if any(sc["id"] == s for sc in pool)]
            remaining = [s for s in pool if s["id"] not in seen_in_theme]
            scenario = (remaining[0] if remaining else pool[0]) if pool else \
                       get_random_scenario(exclude_ids=st.session_state.seen_ids)

        st.session_state.scenario = scenario
        st.session_state.phase = "quiz"
        st.session_state.choix_lettre = None
        st.session_state.choix_texte = None
        st.session_state.chat_messages = []
        if scenario["id"] not in st.session_state.seen_ids:
            st.session_state.seen_ids.append(scenario["id"])
        st.rerun()

    st.markdown("---")

    # Génération d'un nouveau scénario via Mistral + image Pollinations
    st.markdown("### 🤖 Générer un scénario")
    st.caption("Mistral crée une nouvelle situation sur le thème de ton choix.")
    gen_theme = st.text_input(
        "Thème libre",
        placeholder="ex: voisinage, voyage, sport...",
        key="gen_theme_input"
    )

    if st.button("Générer ✨", use_container_width=True):
        if gen_theme.strip():
            with st.spinner("Bulle crée ton scénario... 🫧"):
                try:
                    new_scenario = generate_scenario_with_image(gen_theme.strip())
                    new_id = append_generated_scenario(new_scenario)
                    new_scenario["id"] = new_id
                    st.session_state.scenario = new_scenario
                    st.session_state.phase = "quiz"
                    st.session_state.choix_lettre = None
                    st.session_state.choix_texte = None
                    st.session_state.chat_messages = []
                    st.success(f"Nouveau scénario créé ! (#{new_id})")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")
        else:
            st.warning("Indique un thème pour générer un scénario.")

    st.markdown("---")
    st.caption(f"Scénarios vus : {len(st.session_state.seen_ids)}")

# ── Contenu principal ──────────────────────────────────────────────────────────

st.markdown('<h1 class="main-title">Quiz dans ta bulle 🫧</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Explore des situations du quotidien, à ton rythme, sans jugement.</p>',
            unsafe_allow_html=True)

# ── Expander d'accueil ─────────────────────────────────────────────────────────

with st.expander("💡 \"Quiz dans ta bulle\" - c'est quoi ?", expanded=st.session_state.scenario is None):
    st.markdown("""
    <div class="welcome-block">
        <p style="font-size:1.15rem; font-weight:600; margin-bottom:1.25rem; color:#555;">
            Un espace pour explorer des situations de la vie quotidienne,
            comprendre tes réactions et t'entraîner à communiquer —
            sans pression, sans jugement.
        </p>
        <div class="welcome-step">
            <span class="welcome-step-icon">🎯</span>
            <span><strong>Choisis un thème</strong> dans la barre latérale — amitié, famille,
            réseaux sociaux, vie pro... ou laisse le hasard décider !</span>
        </div>
        <div class="welcome-step">
            <span class="welcome-step-icon">📖</span>
            <span><strong>Lis la situation</strong> proposée et choisis comment tu réagirais
            parmi trois options.</span>
        </div>
        <div class="welcome-step">
            <span class="welcome-step-icon">🫧</span>
            <span><strong>Discute avec Bulle</strong>, ton compagnon bienveillant — il commente
            la situation avec toi et répond à tes questions, sans jamais dire si tu as
            "bien" ou "mal" répondu.</span>
        </div>
        <div class="welcome-step">
            <span class="welcome-step-icon">✨</span>
            <span><strong>Génère de nouveaux scénarios</strong> sur le thème de ton choix
            grâce à l'intelligence artificielle — ils sont sauvegardés et enrichissent
            la base de scénarios pour tout le monde.</span>
        </div>
        <div class="confidentialite-block">
            🔒 <strong>Confidentialité</strong> — Tes réponses et tes conversations avec Bulle
            ne sont jamais sauvegardées. Tout reste dans ta session et disparaît dès que
            tu fermes l'application. Tu es ici dans ta bulle. 🫧
        </div>
    </div>
    <p style="font-size:0.82rem; color:#bbb; text-align:right; margin-top:0.75rem;">
        Une création d'Aga — propulsé par Mistral AI 🇫🇷
    </p>
    """, unsafe_allow_html=True)

# ── État initial — aucun scénario chargé ──────────────────────────────────────

if st.session_state.scenario is None:
    st.markdown("""
    <div style="text-align:center; padding: 2rem 1rem; color: #bbb;">
        <div style="font-size: 3.5rem; margin-bottom: 1rem;">🫧</div>
        <p style="font-size: 1.1rem; font-family: 'Nunito', sans-serif; font-weight: 600;">
            Clique sur <strong>Nouveau scénario</strong> pour commencer !
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Affichage du scénario ──────────────────────────────────────────────────────

scenario = st.session_state.scenario

# Layout en colonnes : Image à gauche, contenu textuel à droite
col_image, col_content = st.columns([1.4, 1.6], gap="medium")

with col_image:
    image_path = get_image_path(scenario["id"])
    image_b64  = get_image_b64(scenario)

    if image_path:
        # Scénario de base — image locale
        st.image(str(image_path), width=300, caption="", output_format="PNG")
    elif image_b64:
        # Scénario généré — image base64 depuis Supabase
        image_bytes = base64.b64decode(image_b64)
        st.image(image_bytes, width=300, caption="", output_format="PNG")
    else:
        # Placeholder si pas d'image disponible
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e8f5e9, #e3f2fd);
                    border-radius: 16px; height: 300px; width: 300px; display: flex;
                    align-items: center; justify-content: center;
                    font-size: 3rem; margin-bottom: 1rem;">
            🫧
        </div>
        """, unsafe_allow_html=True)

with col_content:
    theme_label = get_theme_label(scenario["theme"])
    st.markdown(f"""
    <div class="scenario-card">
        <div class="theme-badge">{theme_label}</div>
        <p style="font-size: 1.25rem; line-height: 1.7; margin: 0; font-weight: 500;">
            {scenario["contexte"]}
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Phase QUIZ ─────────────────────────────────────────────────────────────────

if st.session_state.phase == "quiz":
    st.markdown('<div class="question-section"><h4>👇 Que ferais-tu ?</h4></div>',
                unsafe_allow_html=True)

    options = scenario["options"]
    for lettre, texte in options.items():
        if st.button(f"**{lettre}** — {texte}", use_container_width=True, key=f"opt_{lettre}"):
            st.session_state.choix_lettre = lettre
            st.session_state.choix_texte  = texte
            st.session_state.phase        = "chat"
            st.session_state.chat_messages = []

            first_msg = build_first_user_message(
                scenario["contexte"], lettre, texte
            )
            st.session_state.chat_messages.append(
                {"role": "user", "content": first_msg}
            )
            st.session_state.loading_chat = True
            st.rerun()

# ── Phase CHAT ─────────────────────────────────────────────────────────────────

elif st.session_state.phase == "chat":

    st.markdown(f"""
    <div class="chosen-answer">
        Tu as choisi <strong>{st.session_state.choix_lettre}</strong> :
        « {st.session_state.choix_texte} »
    </div>
    """, unsafe_allow_html=True)

    # Génère la première réponse de Bulle
    if st.session_state.loading_chat:
        with st.spinner("Bulle réfléchit... 🫧"):
            try:
                response = get_bulle_response(st.session_state.chat_messages)
                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                st.session_state.chat_messages.append(
                    {"role": "assistant",
                     "content": f"Oups, je n'ai pas pu répondre pour l'instant 😕 ({e})"}
                )
        st.session_state.loading_chat = False
        st.rerun()

    # Historique du chat
    for msg in st.session_state.chat_messages:
        # Premier message user = message technique, on ne l'affiche pas
        if msg["role"] == "user" and st.session_state.chat_messages.index(msg) == 0:
            continue

        if msg["role"] == "assistant":
            st.markdown(f"""
            <div>
                <div class="chat-label">🫧 Bulle</div>
                <div class="chat-bulle">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div>
                <div class="chat-label" style="text-align:right;">Toi</div>
                <div class="chat-user">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # Zone de saisie
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Réponds à Bulle",
            placeholder="Tu peux réagir, poser une question, partager ce que tu ressens...",
            key="user_message_input"
        )
    with col2:
        st.markdown("<div style='margin-top: 1.75rem;'></div>", unsafe_allow_html=True)
        send = st.button("→", use_container_width=True)

    if send and user_input.strip():
        st.session_state.chat_messages.append(
            {"role": "user", "content": user_input.strip()}
        )
        with st.spinner("Bulle répond... 🫧"):
            try:
                response = get_bulle_response(st.session_state.chat_messages)
                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                st.session_state.chat_messages.append(
                    {"role": "assistant",
                     "content": f"Oups, une erreur est survenue 😕 ({e})"}
                )
        st.rerun()

    st.markdown("---")

    if st.button("🫧 Nouveau scénario →", use_container_width=True, type="primary"):
        scenario = get_random_scenario(exclude_ids=st.session_state.seen_ids)
        st.session_state.scenario = scenario
        st.session_state.phase = "quiz"
        st.session_state.choix_lettre = None
        st.session_state.choix_texte  = None
        st.session_state.chat_messages = []
        if scenario["id"] not in st.session_state.seen_ids:
            st.session_state.seen_ids.append(scenario["id"])
        st.rerun()
