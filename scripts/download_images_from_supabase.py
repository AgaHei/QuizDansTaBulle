#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🖼️ Téléchargeur d'images Supabase
===================================
Télécharge toutes les images stockées en base64 dans Supabase 
et les sauvegarde localement dans assets/images/

Usage: python scripts/download_images_from_supabase.py
"""

import os
import base64
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from utils.supabase_client import fetch_all_scenarios


def download_images_from_supabase(scenario_range=None, force_overwrite=False):
    """
    Télécharge les images depuis Supabase et les sauvegarde localement.
    
    Args:
        scenario_range: tuple (start, end) pour limiter les scénarios (ex: (51, 58))
        force_overwrite: bool, écrase les fichiers existants si True
    """
    
    print("🖼️ Téléchargement des images depuis Supabase")
    print("=" * 50)
    
    # Créer le dossier assets/images s'il n'existe pas
    assets_dir = Path("assets/images")
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Récupérer tous les scénarios
    print("📡 Connexion à Supabase...")
    scenarios = fetch_all_scenarios()
    print(f"✅ {len(scenarios)} scénarios trouvés")
    
    # Filtrer par plage si spécifiée
    if scenario_range:
        start, end = scenario_range
        scenarios = [s for s in scenarios if start <= int(s['id']) <= end]
        print(f"🎯 Filtrage: scénarios {start} à {end} ({len(scenarios)} scénarios)")
    
    downloaded = 0
    skipped = 0
    errors = 0
    
    for scenario in sorted(scenarios, key=lambda x: int(x['id'])):
        scenario_id = scenario['id']
        image_b64 = scenario.get('image_b64')
        
        if not image_b64:
            print(f"  ⚠️  {scenario_id}: Pas d'image base64 en base")
            continue
            
        # Nom du fichier local
        local_filename = f"{scenario_id}.png"
        local_path = assets_dir / local_filename
        
        # Vérifier si le fichier existe déjà
        if local_path.exists() and not force_overwrite:
            print(f"  ⏭️  {scenario_id}: Fichier existe déjà ({local_path})")
            skipped += 1
            continue
        
        try:
            # Décoder l'image base64
            # Supprimer le préfixe data:image/png;base64, s'il existe
            if image_b64.startswith('data:image'):
                image_b64 = image_b64.split(',', 1)[1]
            
            # Décoder et sauvegarder
            image_data = base64.b64decode(image_b64)
            
            with open(local_path, 'wb') as f:
                f.write(image_data)
            
            # Vérifier la taille du fichier
            file_size = len(image_data)
            print(f"  ✅ {scenario_id}: Image téléchargée ({file_size:,} bytes) → {local_path}")
            downloaded += 1
            
        except Exception as e:
            print(f"  ❌ {scenario_id}: Erreur lors du téléchargement - {str(e)}")
            errors += 1
    
    # Résumé
    print("\n" + "=" * 50)
    print(f"📊 Résumé du téléchargement:")
    print(f"   ✅ Téléchargées: {downloaded}")
    print(f"   ⏭️  Ignorées: {skipped}")
    print(f"   ❌ Erreurs: {errors}")
    print(f"📁 Dossier: {assets_dir.absolute()}")
    
    # Lister les fichiers dans le dossier
    png_files = list(assets_dir.glob("*.png"))
    print(f"\n🖼️ Images dans {assets_dir}:")
    for img_file in sorted(png_files, key=lambda x: int(x.stem) if x.stem.isdigit() else 999):
        size = img_file.stat().st_size
        print(f"   📸 {img_file.name} ({size:,} bytes)")


def main():
    """Interface en ligne de commande."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Téléchargeur d'images Supabase")
    parser.add_argument("--range", type=str, help="Plage de scénarios (ex: 51-58)")
    parser.add_argument("--force", action="store_true", help="Écraser les fichiers existants")
    parser.add_argument("--all", action="store_true", help="Télécharger toutes les images")
    
    args = parser.parse_args()
    
    scenario_range = None
    if args.range:
        try:
            start, end = map(int, args.range.split('-'))
            scenario_range = (start, end)
        except ValueError:
            print("❌ Format de plage invalide. Utilisez: --range 51-58")
            sys.exit(1)
    elif not args.all:
        # Par défaut, télécharger les scénarios 51-58
        scenario_range = (51, 58)
        print("📋 Mode par défaut: scénarios 51-58 (utilisez --all pour tout télécharger)")
    
    download_images_from_supabase(scenario_range, args.force)


if __name__ == "__main__":
    main()