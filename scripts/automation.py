"""
Automation - Tâche hebdomadaire de génération d'images DALL-E
-------------------------------------------------------------
Script pour automatiser la génération d'images via tâche planifiée Windows
ou cron Linux/Mac.

Utilisation :
1. Windows Task Scheduler :
   - Créer une tâche basique
   - Déclencher : Hebdomadaire (ex: dimanche 2h du matin)  
   - Action : Démarrer un programme
   - Programme : python
   - Arguments : scripts/weekly_dalle_generation.py
   - Démarrer dans : C:\Users\aheij\Desktop\Quiz Dans Ta Bulle

2. Cron (Linux/Mac) :
   - crontab -e
   - Ajouter : 0 2 * * 0 cd /path/to/project && python scripts/weekly_dalle_generation.py

3. Manuel :
   - python scripts/weekly_dalle_generation.py
"""

import subprocess
import sys
from pathlib import Path

def run_weekly_generation():
    """Execute le script de génération hebdomadaire."""
    script_path = Path(__file__).parent / "weekly_dalle_generation.py"
    
    print("🔄 Lancement de la génération hebdomadaire...")
    
    try:
        result = subprocess.run([
            sys.executable, 
            str(script_path)
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        print("📋 Sortie du script :")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Erreurs :")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution : {e}")
        return False

def setup_windows_task():
    """Génère la commande pour configurer une tâche Windows."""
    project_dir = Path(__file__).parent.parent.resolve()
    python_exe = sys.executable
    
    print("🪟 Configuration pour Windows Task Scheduler :")
    print("=" * 50)
    print(f"Programme/script : {python_exe}")  
    print(f"Arguments : scripts\\weekly_dalle_generation.py")
    print(f"Démarrer dans : {project_dir}")
    print()
    print("Paramètres suggérés :")
    print("- Déclencheur : Hebdomadaire, Dimanche 2h00")
    print("- Conditions : Démarrer seulement si l'ordinateur est branché")
    print("- Paramètres : Arrêter la tâche si elle dure plus de 1 heure")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Automation génération d'images DALL-E")
    parser.add_argument("--run", action="store_true", help="Exécuter la génération maintenant")
    parser.add_argument("--setup-task", action="store_true", help="Afficher les infos pour configurer la tâche")
    
    args = parser.parse_args()
    
    if args.run:
        success = run_weekly_generation()
        sys.exit(0 if success else 1)
    elif args.setup_task:
        setup_windows_task()
    else:
        print("Usage :")
        print("  python scripts/automation.py --run          # Exécuter maintenant")
        print("  python scripts/automation.py --setup-task   # Infos configuration tâche")