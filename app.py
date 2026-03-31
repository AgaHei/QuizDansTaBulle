"""
Quiz dans ta bulle 🫧
----------------------
Application Streamlit d'entraînement aux compétences sociales.
Scénarios interactifs + mini-chat bienveillant avec Mistral (Bulle).
"""

import base64
import streamlit as st
from pathlib import Path

# Configuration de la page en PREMIER (avant tout autre import)
st.set_page_config(
    page_title="Quiz dans ta bulle 🫧",
    page_icon="🫧",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Affichage immédiat pour HF health check
st.markdown('<h1 style="text-align: center; color: #7ec8e3;">Quiz dans ta bulle 🫧</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #aaa;">Explore des situations du quotidien, à ton rythme, sans jugement.</p>', unsafe_allow_html=True)

# Imports lourds en lazy loading uniquement quand nécessaires
@st.cache_resource
def load_modules():
    """Charge les modules seulement quand nécessaire"""
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
        return True
    except Exception as e:
        st.error(f"Erreur de chargement des modules: {e}")
        return False

# Vérification ultra-rapide des services
@st.cache_data
def check_services_fast():
    """Vérification instantanée sans import de modules lourds"""
    try:
        mistral_ok = bool(st.secrets.get("MISTRAL_API_KEY"))
        supabase_ok = bool(st.secrets.get("SUPABASE_URL") and st.secrets.get("SUPABASE_KEY"))
        return mistral_ok, supabase_ok
    except:
        return False, False

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
        "modules_loaded": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

# Vérification des services
mistral_ok, supabase_ok = check_services_fast()

# Afficher immédiatement quelque chose pour satisfaire HF health check
if not st.session_state.modules_loaded:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("🔄 Initialisation de l'application...")
        
        # Tentative de chargement des modules
        if load_modules():
            st.session_state.modules_loaded = True
            st.success("✅ Application prête !")
            st.rerun()
        else:
            st.error("❌ Erreur de chargement - Mode dégradé")
            st.stop()

"""
Quiz dans ta bulle 🫧
----------------------
Application Streamlit d'entraînement aux compétences sociales.
Scénarios interactifs + mini-chat bienveillant avec Mistral (Bulle).
"""

import base64
import streamlit as st
from pathlib import Path

# Configuration de la page en PREMIER
st.set_page_config(
    page_title="Quiz dans ta bulle 🫧",
    page_icon="🫧",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Affichage immédiat du titre pour répondre rapidement
st.markdown('<h1 style="text-align: center; font-size: 2.2rem; background: linear-gradient(135deg, #7ec8e3, #b39ddb); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Quiz dans ta bulle 🫧</h1>', unsafe_allow_html=True)

# Imports avec gestion d'erreur
@st.cache_resource
def load_modules():
    """Charge les modules avec gestion d'erreur"""
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

# Check de configuration rapide
@st.cache_data
def check_config():
    """Vérification rapide de la configuration"""
    try:
        mistral_ok = bool(st.secrets.get("MISTRAL_API_KEY"))
        supabase_ok = bool(st.secrets.get("SUPABASE_URL") and st.secrets.get("SUPABASE_KEY"))
        return mistral_ok, supabase_ok
    except:
        return False, False

# Initialisation
def init_state():
    defaults = {
        "scenario": None,
        "phase": "quiz",
        "choix_lettre": None,
        "choix_texte": None,
        "chat_messages": [],
        "seen_ids": [],
        "loading_chat": False,
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
    with st.spinner("🔄 Chargement des modules..."):
        st.session_state.modules = load_modules()
        if st.session_state.modules:
            st.success("✅ Application prête !")
            st.rerun()
        else:
            st.error("❌ Impossible de charger l'application")
            st.info("💡 Vérifiez que tous les fichiers utils/ sont présents")
            st.stop()

# Interface normale avec modules chargés
modules = st.session_state.modules

# CSS stylé (version COMPLÈTE restaurée)
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

# Sidebar COMPLÈTE avec toutes les fonctionnalités
with st.sidebar:
    st.markdown("## 🫧 Quiz dans ta bulle")
    st.markdown("---")

    # État des services
    col1, col2 = st.columns(2)
    with col1:
        st.success("✅ **Mistral**" if mistral_ok else "❌ **Mistral**")
    with col2:
        st.success("✅ **Supabase**" if supabase_ok else "❌ **Supabase**")
    
    st.markdown("---")
    
    # Sélection thème COMPLÈTE
    st.markdown("### 🎯 Choisir un thème")
    if mistral_ok and supabase_ok:
        themes = ["Aléatoire"] + [modules['get_theme_label'](t) for t in modules['get_all_themes']()]
        theme_choice = st.selectbox("Thème", themes, label_visibility="collapsed")
    else:
        theme_choice = "Démo"
        st.selectbox("Thème", ["Démo"], label_visibility="collapsed", disabled=True)
        
    st.markdown("---")
    
    # Bouton nouveau scénario avec logique COMPLÈTE
    if st.button("✨ Nouveau scénario", use_container_width=True, type="primary"):
        if mistral_ok and supabase_ok:
            with st.spinner("Chargement du scénario... 🫧"):
                if theme_choice == "Aléatoire":
                    scenario = modules['get_random_scenario'](exclude_ids=st.session_state.seen_ids)
                else:
                    # Logique de thème COMPLÈTE restaurée
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
                    if theme_key:
                        pool = modules['get_scenarios_by_theme'](theme_key)
                        seen_in_theme = [s for s in st.session_state.seen_ids
                                         if any(sc["id"] == s for sc in pool)]
                        remaining = [s for s in pool if s["id"] not in seen_in_theme]
                        scenario = (remaining[0] if remaining else pool[0]) if pool else \
                                   modules['get_random_scenario'](exclude_ids=st.session_state.seen_ids)
                    else:
                        scenario = modules['get_random_scenario'](exclude_ids=st.session_state.seen_ids)
        else:
            # Scénario de démo si pas configuré
            scenario = {
                "id": 1,
                "theme": "demo",
                "contexte": "Vous croisez un collègue dans l'ascenseur qui semble stressé avant une présentation importante.",
                "question": "Que faites-vous ?",
                "options": {
                    "A": "Vous lui demandez comment il se sent",
                    "B": "Vous lui souhaitez bonne chance discrètement", 
                    "C": "Vous ne dites rien pour ne pas le déranger"
                },
                "bonne_reponse": "B",
                "commentaire": "Un soutien discret est souvent apprécié dans ces moments."
            }
        
        st.session_state.scenario = scenario
        st.session_state.phase = "quiz"
        st.session_state.choix_lettre = None
        st.session_state.choix_texte = None
        st.session_state.chat_messages = []
        
        # Gestion des scénarios vus RESTAURÉE
        if scenario["id"] not in st.session_state.seen_ids:
            st.session_state.seen_ids.append(scenario["id"])
        st.rerun()

    st.markdown("---")
    
    # GÉNÉRATION de scénarios COMPLÈTE restaurée
    st.markdown("### 🤖 Générer un scénario")
    if mistral_ok:
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
                        new_scenario = modules['generate_scenario_with_image'](gen_theme.strip())
                        new_id = modules['append_generated_scenario'](new_scenario)
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
    else:
        st.caption("⚠️ Mistral requis pour générer de nouveaux scénarios")
        st.text_input("Thème libre", disabled=True, placeholder="Mistral non configuré")
        st.button("Générer ✨", use_container_width=True, disabled=True)

    st.markdown("---")
    st.caption(f"Scénarios vus : {len(st.session_state.seen_ids)}")

# Interface principale COMPLÈTE
if st.session_state.scenario is None:
    st.markdown('<p class="main-subtitle">Explore des situations du quotidien, à ton rythme, sans jugement.</p>', unsafe_allow_html=True)
    
    # ── Expander d'accueil COMPLET restauré ─────────────────────────────────────────────────────────
    with st.expander("💡 \"Quiz dans ta bulle\" - c'est quoi ?", expanded=True):
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
    
    # Message d'accueil
    st.markdown("""
    <div style="text-align:center; padding: 2rem 1rem; color: #bbb;">
        <div style="font-size: 3.5rem; margin-bottom: 1rem;">🫧</div>
        <p style="font-size: 1.1rem; font-family: 'Nunito', sans-serif; font-weight: 600;">
            Clique sur <strong>✨ Nouveau scénario</strong> pour commencer !
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not (mistral_ok and supabase_ok):
        st.warning("⚠️ Configuration incomplète - Mode démo disponible avec fonctionnalités limitées")
        
else:
    # ── AFFICHAGE DU SCÉNARIO COMPLET avec gestion d'images ──────────────────────────────
    scenario = st.session_state.scenario

    # Layout en colonnes : Image à gauche, contenu textuel à droite (RESTAURÉ)
    col_image, col_content = st.columns([1.4, 1.6], gap="medium")

    with col_image:
        if mistral_ok and supabase_ok:
            # Gestion d'images COMPLÈTE restaurée
            image_path = modules['get_image_path'](scenario["id"])
            image_b64 = modules['get_image_b64'](scenario)

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
        else:
            # Placeholder pour mode démo
            st.markdown("""
            <div style="background: linear-gradient(135deg, #e8f5e9, #e3f2fd);
                        border-radius: 16px; height: 300px; width: 300px; display: flex;
                        align-items: center; justify-content: center;
                        font-size: 3rem; margin-bottom: 1rem;">
                🫧
            </div>
            """, unsafe_allow_html=True)

    with col_content:
        # Affichage avec thème label COMPLET
        if mistral_ok and supabase_ok:
            theme_label = modules['get_theme_label'](scenario["theme"])
        else:
            theme_label = scenario.get('theme', 'DEMO').upper()
            
        st.markdown(f"""
        <div class="scenario-card">
            <div class="theme-badge">{theme_label}</div>
            <p style="font-size: 1.25rem; line-height: 1.7; margin: 0; font-weight: 500;">
                {scenario["contexte"]}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # ── AFFICHAGE COMPLET DU SCÉNARIO AVEC IMAGE ──────────────────────────────────
    
    # Contexte du scénario
    st.markdown("#### " + scenario['contexte'])
    
    # Affichage de l'image si elle existe
    if scenario.get('image_url') or scenario.get('image'):
        image_url = scenario.get('image_url') or scenario.get('image')
        try:
            st.image(image_url, caption="Illustration du scénario", use_column_width=True)
        except Exception:
            # Si l'image ne peut pas être affichée, on ignore silencieusement
            pass
    
    # Question du scénario
    st.markdown("#### " + scenario['question'])
    
    # ── PHASES DE L'APPLICATION COMPLÈTES ──────────────────────────────────────────
    
    # Phase Quiz COMPLÈTE
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
        
        # Affichage du commentaire
        st.markdown(f"""
        <div class="chat-bulle">
            <div class="chat-label">🫧 Bulle</div>
            {scenario['commentaire']}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Nouveau scénario", type="primary"):
            st.session_state.scenario = None
            st.rerun()
    
    # Phase Chat COMPLÈTE avec Bulle (si Mistral configuré)
    elif st.session_state.phase == "chat" and mistral_ok:
        
        # Affichage du choix utilisateur
        st.markdown(f"""
        <div class="chosen-answer">
            <strong>Votre choix :</strong> {st.session_state.choix_lettre}) {st.session_state.choix_texte}
        </div>
        """, unsafe_allow_html=True)
        
        # Initialisation du chat
        if not st.session_state.chat_messages:
            with st.spinner("Bulle réfléchit... 🫧"):
                try:
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
                    # Fallback vers commentaire simple
                    st.markdown(f"""
                    <div class="chat-bulle">
                        <div class="chat-label">🫧 Bulle (mode hors ligne)</div>
                        {scenario['commentaire']}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Affichage COMPLET du chat avec styles CSS appropriés
        if st.session_state.chat_messages:
            st.markdown("#### 💬 Conversation avec Bulle")
            
            for i, msg in enumerate(st.session_state.chat_messages):
                if msg["role"] == "assistant":
                    # Message de Bulle avec style complet
                    st.markdown(f"""
                    <div class="chat-bulle">
                        <div class="chat-label">🫧 Bulle</div>
                        {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                elif msg["role"] == "user" and i > 0:  # On affiche pas le premier message technique
                    # Message utilisateur avec style complet
                    st.markdown(f"""
                    <div class="chat-user">
                        <div class="chat-label" style="text-align: right;">Vous</div>
                        {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Input utilisateur COMPLET
        user_input = st.chat_input("Écrivez à Bulle...")
        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            with st.spinner("Bulle répond... 🫧"):
                try:
                    response = modules['get_bulle_response'](st.session_state.chat_messages)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
                    # Retirer le message utilisateur en cas d'erreur
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
