"""
Quiz dans ta bulle — Client Supabase
--------------------------------------
Gère la connexion et toutes les opérations CRUD sur la table scenarios.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# ── Initialisation ─────────────────────────────────────────────────────────────

def get_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("❌ SUPABASE_URL ou SUPABASE_KEY introuvable — vérifie ton .env")
    return create_client(url, key)


# ── Lecture ────────────────────────────────────────────────────────────────────

def fetch_all_scenarios() -> list[dict]:
    """Retourne tous les scénarios depuis Supabase, ordonnés par id."""
    client = get_client()
    response = client.table("scenarios").select("*").order("id").execute()
    return response.data


def fetch_scenario_by_id(scenario_id: str) -> dict | None:
    """Retourne un scénario par son id, ou None s'il n'existe pas."""
    client = get_client()
    response = (
        client.table("scenarios")
        .select("*")
        .eq("id", scenario_id)
        .execute()
    )
    return response.data[0] if response.data else None


def fetch_scenarios_by_theme(theme: str) -> list[dict]:
    """Retourne tous les scénarios d'un thème donné."""
    client = get_client()
    response = (
        client.table("scenarios")
        .select("*")
        .eq("theme", theme)
        .order("id")
        .execute()
    )
    return response.data


# ── Écriture ───────────────────────────────────────────────────────────────────

def insert_scenario(scenario: dict) -> dict:
    """
    Insère un nouveau scénario dans Supabase.
    Retourne le scénario inséré avec son id.
    """
    client = get_client()
    response = client.table("scenarios").insert(scenario).execute()
    return response.data[0]


def update_scenario_image(scenario_id: str, image_b64: str) -> None:
    """Met à jour le champ image_b64 d'un scénario existant."""
    client = get_client()
    client.table("scenarios").update(
        {"image_b64": image_b64}
    ).eq("id", scenario_id).execute()


# ── Utilitaires ────────────────────────────────────────────────────────────────

def get_next_id() -> str:
    """
    Calcule le prochain id disponible (format '051', '052'...).
    """
    scenarios = fetch_all_scenarios()
    if not scenarios:
        return "001"
    max_id = max(int(s["id"]) for s in scenarios)
    return str(max_id + 1).zfill(3)


def scenario_exists(scenario_id: str) -> bool:
    """Vérifie si un scénario existe déjà dans Supabase."""
    return fetch_scenario_by_id(scenario_id) is not None
