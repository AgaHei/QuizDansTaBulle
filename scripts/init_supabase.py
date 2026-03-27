"""
Quiz dans ta bulle — Initialisation Supabase
----------------------------------------------
Script ONE-SHOT à lancer UNE SEULE FOIS pour peupler Supabase
avec les 50 scénarios de base depuis scenarios.json.

Usage :
    python scripts/init_supabase.py
"""

import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from utils.supabase_client import get_client, scenario_exists

SCENARIOS_PATH = Path("data/scenarios.json")

# ── Chargement du JSON ─────────────────────────────────────────────────────────

with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

scenarios = data["quiz"]
total = len(scenarios)

print(f"🫧 Initialisation Supabase — {total} scénarios à importer\n")

# ── Insertion ──────────────────────────────────────────────────────────────────

client = get_client()
inserted = 0
skipped = 0
errors = []

for scenario in scenarios:
    sid = scenario["id"]

    # Ne pas réinsérer si déjà présent
    if scenario_exists(sid):
        print(f"  ⏭️  Scénario {sid} déjà présent — ignoré")
        skipped += 1
        continue

    try:
        # Formate le scénario pour Supabase
        # (options est un dict → stocké en JSONB)
        row = {
            "id":           sid,
            "theme":        scenario["theme"],
            "contexte":     scenario["contexte"],
            "question":     scenario["question"],
            "options":      scenario["options"],
            "bonne_reponse":scenario["bonne_reponse"],
            "commentaire":  scenario["commentaire"],
            "image_prompt": scenario.get("image_prompt", ""),
            "image_b64":    None,   # images de base servies depuis assets/
            "source":       "base",
        }

        client.table("scenarios").insert(row).execute()
        print(f"  ✅ Scénario {sid} inséré")
        inserted += 1

    except Exception as e:
        print(f"  ❌ Scénario {sid} — erreur : {e}")
        errors.append({"id": sid, "error": str(e)})

# ── Rapport ────────────────────────────────────────────────────────────────────

print(f"\n{'─'*50}")
print(f"✅ Insérés  : {inserted}")
print(f"⏭️  Ignorés  : {skipped}")
print(f"❌ Erreurs  : {len(errors)}")

if errors:
    print("\nScénarios en erreur :")
    for err in errors:
        print(f"  - {err['id']} : {err['error']}")
    print("\nRelance le script — les scénarios déjà insérés seront ignorés.")

print("\n🫧 Supabase prêt !")
