# 🎨 Système de génération d'images DALL-E hebdomadaire

## 🎯 Principe

Ce système permet de générer automatiquement des images de qualité professionnelle pour tous les nouveaux scénarios créés via Mistral, en utilisant DALL-E payant de manière optimisée (hebdomadaire).

## 📋 Workflow complet

### 1. **Création de nouveaux scénarios** (temps réel)
- Utilisateur crée un scénario via Mistral AI
- Scénario sauvé dans Supabase avec `image_b64 = null`
- Interface affiche le **placeholder 🫧** (expérience immédiate)

### 2. **Génération d'images** (hebdomadaire)  
- Script `weekly_dalle_generation.py` détecte les nouveaux scénarios
- Génère des images DALL-E de qualité pour chaque scénario
- **Double sauvegarde** :
  - 📁 Local : `assets/images/generated/{id}.png`
  - 💾 Supabase : `image_b64` field

### 3. **Affichage intelligent** (priorité)
```
1. assets/images/generated/{id}.png    ← Images DALL-E (qualité max)
2. assets/images/scenario_{id}.png     ← Images originales 
3. Supabase image_b64                  ← Backup si local manqué
4. Placeholder 🫧                      ← Fallback élégant
```

## 📂 Structure des fichiers

```
assets/
├── images/
│   ├── scenario_001.png              # Images originales (001-051)
│   ├── scenario_002.png
│   └── generated/                     # 🆕 Images DALL-E hebdomadaires
│       ├── 052.png                    # Premier scénario généré
│       ├── 053.png
│       └── ...
scripts/
├── weekly_dalle_generation.py        # 🎨 Génération DALL-E principale
├── automation.py                     # ⏰ Configuration tâches auto
└── ...
generation_log.json                   # 📋 Historique générations
```

## 🚀 Utilisation

### Test de simulation (gratuit)
```bash
python simulate_dalle_generation.py
```

### Génération réelle DALL-E (payant)
```bash
python scripts/weekly_dalle_generation.py
```

### Configuration automatique
```bash
# Voir les infos pour configurer la tâche Windows
python scripts/automation.py --setup-task

# Exécuter via automation
python scripts/automation.py --run
```

## ⚙️ Configuration requise

### Variables d'environnement (.env)
```env
OPENAI_API_KEY=sk-...                 # Clé API OpenAI pour DALL-E
MISTRAL_API_KEY=...                   # Déjà configuré
SUPABASE_URL=...                      # Déjà configuré  
SUPABASE_KEY=...                      # Déjà configuré
```

### Coûts DALL-E 3
- **Standard 1024x1024** : ~$0.040 par image
- **Exemple** : 10 nouveaux scénarios = ~$0.40 USD
- **Budget mensuel suggéré** : $5-10 USD

## 📅 Automation suggestions

### Windows Task Scheduler
- **Fréquence** : Hebdomadaire (ex: Dimanche 2h00)
- **Conditions** : Ordinateur branché + connecté Internet
- **Timeout** : 1 heure maximum

### Cron (Linux/Mac)
```bash
# Tous les dimanches à 2h00
0 2 * * 0 cd /path/to/project && python scripts/weekly_dalle_generation.py
```

## 🧪 Tests et validation

### Test de priorisation
```bash
python test_image_priority.py
```

### Test de classification thème
```bash
python test_theme_classification.py
```

### Simulation complète
1. `python simulate_dalle_generation.py` (crée des images factices)
2. Relancer l'app Streamlit
3. Vérifier que les nouveaux scénarios ont des images

## 💡 Avantages du système

1. **🚀 Expérience utilisateur** : Pas d'attente lors de création
2. **💰 Coût optimisé** : Génération groupée vs individuelle  
3. **🔄 Fiabilité** : Double sauvegarde local + cloud
4. **🎨 Qualité** : Images DALL-E professionnelles
5. **⚡ Performance** : Images locales = chargement instantané
6. **📊 Contrôle** : Logs et historique des générations

## 🔧 Maintenance

- **Vérifier les logs** : `generation_log.json`
- **Surveiller les coûts** : Dashboard OpenAI
- **Backup images** : Synchroniser `assets/images/generated/`
- **Nettoyage** : Supprimer les anciennes images si nécessaire

---

**✨ Système prêt ! Créez des scénarios en temps réel, les images arriveront automatiquement chaque semaine.**