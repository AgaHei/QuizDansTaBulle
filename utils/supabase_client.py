"""
Quiz dans ta bulle — Client Supabase
--------------------------------------
Gère la connexion et toutes les opérations CRUD sur la table scenarios.
"""

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# ── Initialisation avec gestion d'erreur robuste ──────────────────────────────

def get_client() -> Client:
    """Retourne le client Supabase avec gestion d'erreur"""
    try:
        # Priorité à st.secrets (déploiement) puis .env (local)
        url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            return None  # Pas d'erreur, juste pas configuré
        
        return create_client(url, key)
    except Exception:
        return None  # Silencieux en cas d'erreur de connexion

# ── Données de fallback ────────────────────────────────────────────────────────

FALLBACK_SCENARIOS = [
    {
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
    },
    {
        "id": "002", 
        "contexte": "Ton ami(e) te raconte ses problèmes familiaux depuis 20 minutes. Tu commences à te sentir dépassé(e) et tu ne sais pas quoi dire.",
        "question": "Que fais-tu ?",
        "options": {
            "A": "Je continue d'écouter même si je me sens mal à l'aise",
            "B": "Je lui dis gentiment que j'ai besoin d'une pause",
            "C": "Je essaie de donner des conseils pour l'aider",
            "D": "Je partage mes propres problèmes pour créer un équilibre"
        },
        "commentaire": "Écouter c'est important, mais prendre soin de son propre bien-être aussi. Il est ok de poser des limites bienveillantes.",
        "theme": "amitie"
    },
    {
        "id": "003",
        "contexte": "Tu es au supermarché et tu vois qu'une personne âgée a du mal à atteindre un produit sur une étagère haute.",
        "question": "Que fais-tu ?",
        "options": {
            "A": "Je m'approche directement pour l'aider",
            "B": "J'attends qu'elle me demande de l'aide",
            "C": "Je demande d'abord si elle a besoin d'aide",
            "D": "Je fais semblant de ne rien voir"
        },
        "commentaire": "Proposer son aide avec respect est toujours apprécié. Demander d'abord permet à la personne de garder son autonomie.",
        "theme": "quotidien"
    }
]

# ── Lecture avec fallback ──────────────────────────────────────────────────────

def fetch_all_scenarios() -> list[dict]:
    """Retourne tous les scénarios depuis Supabase, avec fallback par défaut."""
    client = get_client()
    if not client:
        return FALLBACK_SCENARIOS
        
    try:
        # Chargement par pagination pour éviter le timeout
        all_scenarios = []
        page_size = 15  # Optimisé pour réduire les appels tout en évitant les timeouts
        offset = 0
        
        while True:
            # Charge une page de scénarios
            response = client.table("scenarios").select("*").order("id").range(offset, offset + page_size - 1).execute()
            
            if not response.data:
                break
                
            all_scenarios.extend(response.data)
            print(f"DEBUG: Page chargée {len(response.data)} scénarios (total: {len(all_scenarios)})")
            
            # Si moins de page_size résultats, c'est la dernière page
            if len(response.data) < page_size:
                break
                
            offset += page_size
            
        print(f"DEBUG: TOTAL récupéré {len(all_scenarios)} scénarios depuis Supabase")
        return all_scenarios if all_scenarios else FALLBACK_SCENARIOS
    except Exception as e:
        # En cas d'erreur, on retourne ce qu'on a déjà récupéré s'il y en a
        if 'all_scenarios' in locals() and all_scenarios:
            print(f"DEBUG: Erreur Supabase mais conservation de {len(all_scenarios)} scénarios déjà récupérés")
            return all_scenarios
        else:
            # Timeout ou autre erreur → fallback silencieux
            print(f"DEBUG: Erreur Supabase - {type(e).__name__}: {e}")
            return FALLBACK_SCENARIOS

def fetch_scenario_by_id(scenario_id: str) -> dict | None:
    """Retourne un scénario par son id, ou None s'il n'existe pas."""
    client = get_client()
    if not client:
        # Chercher dans les données de fallback
        for scenario in FALLBACK_SCENARIOS:
            if scenario['id'] == scenario_id:
                return scenario
        return None
        
    try:
        response = (
            client.table("scenarios")
            .select("*")
            .eq("id", scenario_id)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception:
        return None

def fetch_scenarios_by_theme(theme: str) -> list[dict]:
    """Retourne tous les scénarios d'un thème donné."""
    client = get_client()
    if not client:
        # Filtrer les données de fallback par thème
        return [s for s in FALLBACK_SCENARIOS if s['theme'] == theme]
        
    try:
        response = (
            client.table("scenarios")
            .select("*")
            .eq("theme", theme)
            .order("id")
            .execute()
        )
        return response.data if response.data else []
    except Exception:
        return [s for s in FALLBACK_SCENARIOS if s['theme'] == theme]

# ── Écriture ───────────────────────────────────────────────────────────────────

def insert_scenario(scenario: dict) -> dict:
    """
    Insère un nouveau scénario dans Supabase.
    Retourne le scénario inséré avec son id.
    """
    client = get_client()
    if not client:
        st.error("❌ Insertion impossible - Supabase non configuré")
        return scenario
        
    try:
        response = client.table("scenarios").insert(scenario).execute()
        return response.data[0]
    except Exception as e:
        st.error(f"❌ Erreur d'insertion: {e}")
        return scenario

def update_scenario_image(scenario_id: str, image_b64: str) -> None:
    """Met à jour le champ image_b64 d'un scénario existant."""
    client = get_client()
    if not client:
        st.error("❌ Mise à jour impossible - Supabase non configuré")
        return
        
    try:
        client.table("scenarios").update(
            {"image_b64": image_b64}
        ).eq("id", scenario_id).execute()
    except Exception as e:
        st.error(f"❌ Erreur de mise à jour: {e}")

# ── Utilitaires ────────────────────────────────────────────────────────────────

def get_next_id() -> str:
    """
    Calcule le prochain id disponible (format '051', '052'...).
    """
    try:
        scenarios = fetch_all_scenarios()
        if not scenarios:
            return "001"
        max_id = max(int(s["id"]) for s in scenarios)
        return str(max_id + 1).zfill(3)
    except Exception:
        return "999"  # ID de fallback

def scenario_exists(scenario_id: str) -> bool:
    """Vérifie si un scénario existe déjà dans Supabase."""
    return fetch_scenario_by_id(scenario_id) is not None
