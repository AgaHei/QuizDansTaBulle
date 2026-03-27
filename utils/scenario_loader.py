"""
Quiz dans ta bulle — Chargement et gestion des scénarios
---------------------------------------------------------
Lit les scénarios depuis Supabase.
Les images des scénarios de base sont servies depuis assets/images/.
Les images des scénarios générés sont stockées en base64 dans Supabase.
"""

import random
from pathlib import Path
from utils.supabase_client import (
    fetch_all_scenarios,
    fetch_scenarios_by_theme,
    insert_scenario,
    get_next_id,
)

IMAGES_DIR = Path("assets/images")

# ── Scénarios ──────────────────────────────────────────────────────────────────

def load_scenarios() -> list[dict]:
    """Charge et retourne tous les scénarios depuis Supabase."""
    return fetch_all_scenarios()


def get_random_scenario(exclude_ids: list[str] = None) -> dict:
    """
    Retourne un scénario aléatoire en excluant les ids déjà vus.
    Si tous ont été vus, recommence depuis le début.
    """
    scenarios = load_scenarios()
    if exclude_ids:
        remaining = [s for s in scenarios if s["id"] not in exclude_ids]
        if not remaining:
            remaining = scenarios
    else:
        remaining = scenarios
    return random.choice(remaining)


def get_scenarios_by_theme(theme: str) -> list[dict]:
    """Retourne tous les scénarios d'un thème donné."""
    return fetch_scenarios_by_theme(theme)


def get_all_themes() -> list[str]:
    """Retourne uniquement les thèmes prédéfinis pour une expérience cohérente."""
    # Thèmes fixes - ne pas ajouter les thèmes générés par Mistral
    return ["ecole", "amitie", "famille", "quotidien", "reseaux_sociaux", "pro", "relations"]

# ── Images ─────────────────────────────────────────────────────────────────────

def get_image_path(scenario_id: str) -> Path | None:
    """
    Retourne le chemin de l'image locale avec priorité :
    1. Images DALL-E générées (assets/images/generated/)
    2. Images originales (assets/images/)  
    """
    # Priorité 1 : Images DALL-E générées hebdomadairement
    generated_path = IMAGES_DIR / "generated" / f"{scenario_id}.png"
    if generated_path.exists():
        return generated_path
    
    # Priorité 2 : Images originales (scénarios 001-051)
    original_path = IMAGES_DIR / f"scenario_{scenario_id}.png"
    if original_path.exists():
        return original_path
    
    return None


def has_local_image(scenario_id: str) -> bool:
    """Vérifie si une image locale existe (originale ou générée)."""
    return get_image_path(scenario_id) is not None


def get_image_b64(scenario: dict) -> str | None:
    """
    Retourne l'image en base64 depuis Supabase si aucune image locale n'existe.
    Logique de priorité : Local > Base64 > Placeholder
    """
    scenario_id = scenario["id"]
    
    # Si une image locale existe, ne pas utiliser la base64
    if has_local_image(scenario_id):
        return None
    
    # Sinon, utiliser l'image base64 depuis Supabase (peut être None)
    return scenario.get("image_b64")

# ── Labels des thèmes ──────────────────────────────────────────────────────────

THEME_LABELS = {
    "ecole":           "🏫 École & formation",
    "amitie":          "👫 Amitié & groupe",
    "famille":         "👨‍👩‍👧 Famille",
    "quotidien":       "🏙️ Vie quotidienne",
    "reseaux_sociaux": "📱 Réseaux sociaux",
    "pro":             "💼 Vie pro & stages",
    "relations":       "❤️ Relations",
}

def get_theme_label(theme: str) -> str:
    return THEME_LABELS.get(theme, theme.capitalize())

# ── Ajout de scénarios générés ─────────────────────────────────────────────────

def append_generated_scenario(scenario: dict) -> str:
    """
    Insère un scénario généré par Mistral dans Supabase.
    Génère automatiquement un nouvel id et le retourne.
    """
    new_id = get_next_id()
    scenario["id"] = new_id
    scenario["source"] = "generated"

    if "image_b64" not in scenario:
        scenario["image_b64"] = None

    insert_scenario(scenario)
    return new_id
