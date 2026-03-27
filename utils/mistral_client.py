"""
Quiz dans ta bulle — Client Mistral + génération d'images HuggingFace
----------------------------------------------------------------------
Gère le prompt système, les appels Mistral, la génération de scénarios
et la génération d'images via HuggingFace Inference API (FLUX.1-schnell).
"""

import os
import json
import base64
import requests
from mistralai.client import Mistral
from dotenv import load_dotenv

load_dotenv()

# ── Initialisation Mistral ─────────────────────────────────────────────────────

def get_client() -> Mistral:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("❌ MISTRAL_API_KEY introuvable — vérifie ton .env")
    return Mistral(api_key=api_key)

MODEL = "mistral-small-latest"

# ── Prompt système ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Tu es Bulle, un compagnon bienveillant et curieux dans l'application "Quiz dans ta bulle".

Ton rôle est d'accompagner l'utilisateur après qu'il a choisi sa réponse à une situation sociale. 
Tu commentes la situation avec chaleur, sans jamais juger ni évaluer — même si la réponse choisie 
n'était pas la plus adaptée. Tu ouvres ensuite un espace de conversation où l'utilisateur peut 
explorer ses propres réactions, ressentis et questions.

## Qui tu es

- Tu es doux(ce), drôle parfois, jamais moralisateur(trice)
- Tu parles comme un(e) ami(e) sincère, pas comme un prof ou un psy
- Tu t'adresses à des jeunes et adultes de tous horizons
- Tu utilises "tu" naturellement, avec respect et simplicité
- Tu n'es jamais condescendant(e) — chaque réaction est valide

## Ce que tu fais

Quand l'utilisateur partage son choix dans une situation sociale, tu :

1. **Accueilles** son choix sans verdict ("bien" / "mal" / "correct" sont bannis de ton vocabulaire)
2. **Explores** la situation avec curiosité : pourquoi cette réaction est humaine, ce qu'elle dit 
   de nos besoins, nos peurs, nos valeurs
3. **Proposes** doucement une autre façon de voir les choses, si c'est utile — jamais comme 
   une correction, toujours comme une invitation
4. **Invites** l'utilisateur à continuer la conversation s'il le souhaite

## Ce que tu ne fais jamais

- Tu ne dis jamais que c'est la "bonne" ou la "mauvaise" réponse
- Tu ne fais pas la leçon
- Tu n'utilises pas de jargon thérapeutique ou psychologique
- Tu ne poses pas plusieurs questions à la fois — une seule, ouverte et simple
- Tu ne termines pas chaque message par une question si ce n'est pas naturel
- Tu n'es jamais trop long(ue) — tes réponses font 3 à 6 phrases maximum

## Ton style

- Chaleureux, spontané, légèrement poétique parfois
- Phrases courtes, langage naturel — comme à l'oral
- Une touche d'humour subtil quand la situation s'y prête
- Toujours en français

## Format du premier message

Ton premier message doit :
- Commencer par accueillir le choix de façon naturelle (jamais par "Bien sûr !" ou "Absolument !")
- Donner en 2-3 phrases une réflexion douce sur cette situation
- Terminer par une invitation ouverte à échanger, si ça te semble naturel

Rappelle-toi : tu n'es pas là pour enseigner, tu es là pour réfléchir ensemble. 🫧
"""

# ── Construction du premier message ───────────────────────────────────────────

def build_first_user_message(contexte: str, choix_lettre: str, choix_texte: str) -> str:
    return (
        f"Situation : {contexte}\n\n"
        f"J'ai choisi la réponse {choix_lettre} : « {choix_texte} »"
    )

# ── Appel API Mistral ──────────────────────────────────────────────────────────

def get_bulle_response(messages: list[dict]) -> str:
    """Envoie l'historique à Mistral et retourne la réponse de Bulle."""
    client = get_client()
    full_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *messages
    ]
    response = client.chat.complete(
        model=MODEL,
        messages=full_messages,
        max_tokens=300,
        temperature=0.75,
    )
    return response.choices[0].message.content.strip()

# ── Génération de scénarios ────────────────────────────────────────────────────

SCENARIO_GENERATION_PROMPT = """Tu es un créateur de contenu pour "Quiz dans ta bulle", 
une application bienveillante d'entraînement aux compétences sociales pour jeunes et adultes.

Génère un nouveau scénario de quiz en français sur le thème demandé.
Réponds UNIQUEMENT avec un JSON valide, sans texte avant ni après, sans balises markdown.

Format exact :
{
  "theme": "nom_du_theme",
  "contexte": "Description courte et concrète de la situation sociale (2-3 phrases max)",
  "question": "Que fais-tu dans cette situation ?",
  "options": {
    "A": "Première réponse possible",
    "B": "Deuxième réponse possible",
    "C": "Troisième réponse possible"
  },
  "bonne_reponse": "A",
  "commentaire": "Explication bienveillante de la réponse suggérée (2-3 phrases, ton chaleureux)",
  "image_prompt": "Cartoon comic style illustration, fun and expressive, clean lines, vibrant playful colours, diverse characters of various ages, warm and inclusive atmosphere, no text, no labels, digital illustration. [description spécifique de la scène en anglais]"
}

Règles importantes :
- La situation doit être universelle et reconnaissable
- Les trois réponses doivent être plausibles — pas de réponse évidemment absurde
- Le commentaire ne doit jamais utiliser les mots "correct", "bien", "mal", "erreur"
- Le ton est toujours chaleureux, jamais moralisateur
"""

def classify_theme_from_user_input(user_theme: str) -> str:
    """
    Classifie un thème libre d'utilisateur vers les catégories prédéfinies.
    """
    theme_mapping = {
        # Famille (plus spécifique en premier)
        "famille": ["famille", "parent", "frère", "sœur", "enfant", "familial", "maison", "foyer", "parents"],
        # École & formation
        "ecole": ["école", "éducation", "cours", "classe", "étudiant", "professeur", "formation", "université", "collège", "lycée", "scolaire"],
        # Vie pro & stages
        "pro": ["travail", "professionnel", "stage", "entreprise", "bureau", "job", "carrière", "collègue", "boulot"],
        # Réseaux sociaux
        "reseaux_sociaux": ["réseaux sociaux", "internet", "en ligne", "digital", "réseaux", "web", "social media", "facebook", "instagram"],
        # Amitié & groupe (après famille pour éviter confusion)
        "amitie": ["amitié", "ami", "groupe", "social", "copain", "relations sociales", "camarade", "amis"],
        # Relations
        "relations": ["relation", "couple", "amour", "rencontre", "sentiments", "romantique", "petit ami", "petite amie"],
        # Vie quotidienne (en dernier, catch-all)
        "quotidien": ["quotidien", "vie courante", "routine", "transport", "magasin", "voisin", "rue", "public", "ville"]
    }
    
    user_theme_lower = user_theme.lower()
    
    # Recherche par mots-clés
    for category, keywords in theme_mapping.items():
        if any(keyword in user_theme_lower for keyword in keywords):
            return category
    
    # Par défaut : quotidien
    return "quotidien"


def generate_new_scenario(theme: str) -> dict:
    """Génère un scénario texte via Mistral."""
    client = get_client()
    response = client.chat.complete(
        model=MODEL,
        messages=[
            {"role": "system", "content": SCENARIO_GENERATION_PROMPT},
            {"role": "user", "content": f"Génère un scénario sur le thème : {theme}"}
        ],
        max_tokens=600,
        temperature=0.85,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

# ── Génération d'image via Placeholder.pics + style ──────────────────────────

def generate_image_b64(image_prompt: str) -> str | None:
    """
    Génère un placeholder d'image cohérent basé sur le prompt Mistral.
    Retourne None pour afficher le placeholder 🫧 dans l'app.
    
    Note: Les vraies API d'images sont soit payantes soit instables.
    On utilise des placeholders pour une expérience homogène.
    """
    print(f"  🎨 Placeholder généré pour prompt Mistral")
    print(f"  ℹ️ Les images des nouveaux scénarios utilisent le placeholder 🫧")
    
    # Retourne None pour utiliser le placeholder 🫧 dans l'interface
    return None


def generate_scenario_with_image(theme: str) -> dict:
    """
    Génère un scénario complet (texte Mistral + image + thème classifié).
    Retourne un dict prêt pour Supabase avec une catégorie appropriée.
    """
    # 1. Génère le scénario texte via Mistral
    scenario = generate_new_scenario(theme)

    # 2. Classification automatique du thème
    classified_theme = classify_theme_from_user_input(theme)
    scenario["theme"] = classified_theme

    # 3. Génère l'image thématique
    image_prompt = scenario.get("image_prompt", "")
    scenario["image_b64"] = generate_image_b64(image_prompt) if image_prompt else None

    return scenario
