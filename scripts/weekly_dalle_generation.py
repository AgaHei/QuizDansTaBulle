"""
Quiz dans ta bulle — Génération d'images DALL-E hebdomadaire
------------------------------------------------------------
Script pour générer des images de qualité pour tous les nouveaux scénarios
créés depuis la dernière génération. Sauvegarde en local + Supabase.

Usage :
    python scripts/weekly_dalle_generation.py
    
Prérequis :
    - OPENAI_API_KEY dans .env
    - Crédits DALL-E disponibles
"""

import os
import json
import base64
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils.supabase_client import fetch_all_scenarios, update_scenario_image

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────

DALLE_MODEL = "dall-e-3"
IMAGE_SIZE = "1024x1024"
IMAGE_QUALITY = "hd"
IMAGES_DIR = Path("assets/images")
GENERATION_LOG = Path("generation_log.json")

# ── Utilitaires ────────────────────────────────────────────────────────────────

def load_generation_log():
    """Charge l'historique des générations."""
    if GENERATION_LOG.exists():
        with open(GENERATION_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_generation": None, "generated_scenarios": []}

def save_generation_log(log_data):
    """Sauvegarde l'historique des générations."""
    with open(GENERATION_LOG, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

def get_scenarios_needing_images(since_date=None):
    """Retourne les scénarios générés qui n'ont pas d'images locales."""
    scenarios = fetch_all_scenarios()
    
    needing_images = []
    for scenario in scenarios:
        # Ne traiter que les scénarios générés (pas les originaux 001-051)
        if scenario.get("source") == "generated":
            scenario_id = scenario["id"]
            
            # Vérifier si l'image locale existe (nomenclature scenario_XXX.png)
            local_path = IMAGES_DIR / f"scenario_{scenario_id}.png"
            if not local_path.exists():
                # Filtrer par date si spécifié
                if since_date:
                    # Tu peux ajouter un champ created_at dans Supabase pour filtrer
                    # Pour l'instant, on traite tous les scénarios sans images
                    pass
                needing_images.append(scenario)
    
    return needing_images

# ── Génération DALL-E ──────────────────────────────────────────────────────────

def generate_dalle_image(prompt, scenario_id):
    """Génère une image via DALL-E 3 et la sauvegarde localement."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY manquante dans .env")
    
    print(f"  🎨 Génération DALL-E pour prompt : {prompt[:60]}...")
    
    # Appel API DALL-E
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": DALLE_MODEL,
        "prompt": prompt,
        "size": IMAGE_SIZE,  
        "quality": IMAGE_QUALITY,
        "n": 1
    }
    
    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=headers,
        json=data,
        timeout=120
    )
    response.raise_for_status()
    
    result = response.json()
    image_url = result["data"][0]["url"]
    
    # Télécharger l'image
    print(f"  ⬇️ Téléchargement de l'image...")
    img_response = requests.get(image_url, timeout=60)
    img_response.raise_for_status()
    
    # Sauvegarder localement avec nomenclature scenario_XXX.png
    IMAGES_DIR.mkdir(exist_ok=True)
    local_path = IMAGES_DIR / f"scenario_{scenario_id}.png"
    
    with open(local_path, "wb") as f:
        f.write(img_response.content)
    
    # Encoder en base64 pour Supabase
    image_b64 = base64.b64encode(img_response.content).decode("utf-8")
    
    print(f"  ✅ Image sauvée : {local_path} ({len(img_response.content)} bytes)")
    return image_b64

# ── Script principal ───────────────────────────────────────────────────────────

def main():
    print("🎨 Génération d'images DALL-E hebdomadaire")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Charger l'historique
    log_data = load_generation_log()
    last_gen = log_data.get("last_generation")
    
    if last_gen:
        print(f"📋 Dernière génération : {last_gen}")
    else:
        print("📋 Première génération")
    
    # Trouver les scénarios nécessitant des images
    scenarios = get_scenarios_needing_images()
    
    if not scenarios:
        print("✅ Aucun nouveau scénario à traiter !")
        return
    
    print(f"🎯 {len(scenarios)} scénarios sans images trouvés")
    print()
    
    # Confirmation avant génération (coût !)
    total_cost = len(scenarios) * 0.040  # DALL-E 3 standard ~4¢
    print(f"💰 Coût estimé : ~${total_cost:.2f} USD")
    
    confirm = input("Continuer ? (oui/non) : ").lower()
    if confirm not in ["oui", "o", "yes", "y"]:
        print("❌ Génération annulée")
        return
    
    print("\n🚀 Démarrage de la génération...")
    print("=" * 50)
    
    generated_count = 0
    errors = []
    
    for i, scenario in enumerate(scenarios, 1):
        scenario_id = scenario["id"]
        image_prompt = scenario.get("image_prompt", "")
        
        if not image_prompt:
            print(f"[{i}/{len(scenarios)}] Scénario {scenario_id} - ⚠️ Pas de prompt, ignoré")
            continue
            
        print(f"[{i}/{len(scenarios)}] Scénario {scenario_id}")
        
        try:
            # Génération DALL-E + sauvegarde locale
            image_b64 = generate_dalle_image(image_prompt, scenario_id)
            
            # Mise à jour Supabase 
            update_scenario_image(scenario_id, image_b64)
            print(f"  💾 Base de données mise à jour")
            
            # Mise à jour du log
            log_data["generated_scenarios"].append({
                "id": scenario_id,
                "generated_at": datetime.now().isoformat(),
                "prompt": image_prompt[:100] + "..." if len(image_prompt) > 100 else image_prompt
            })
            
            generated_count += 1
            
        except Exception as e:
            error_msg = f"Erreur scénario {scenario_id}: {e}"
            print(f"  ❌ {error_msg}")
            errors.append(error_msg)
        
        print()
    
    # Finalisation
    log_data["last_generation"] = datetime.now().isoformat()
    save_generation_log(log_data)
    
    print("🎉 Génération terminée !")
    print(f"  ✅ Images générées : {generated_count}")
    print(f"  ❌ Erreurs : {len(errors)}")
    
    if errors:
        print("\n⚠️ Erreurs détaillées :")
        for error in errors:
            print(f"  • {error}")
    
    print(f"\n💰 Coût réel estimé : ~${generated_count * 0.040:.2f} USD")

if __name__ == "__main__":
    main()