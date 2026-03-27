# 🫧 Quiz dans ta bulle

> Application interactive d'entraînement aux compétences sociales, propulsée par Mistral AI et déployée sur HuggingFace Spaces.

[![HuggingFace](https://img.shields.io/badge/🤗%20HuggingFace-Quiz%20dans%20ta%20bulle-blue)](https://huggingface.co/spaces/TON_USERNAME/quiz-dans-ta-bulle)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)](https://streamlit.io)
[![Mistral AI](https://img.shields.io/badge/Mistral%20AI-mistral--small-orange)](https://mistral.ai)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green)](https://supabase.com)

---

## 🎯 Concept

Quiz dans ta bulle propose des scénarios de la vie quotidienne (amitié, famille, travail, réseaux sociaux...) et invite l'utilisateur à explorer ses réactions sociales avec **Bulle**, un compagnon IA bienveillant.

L'application est conçue pour être inclusive et non-clinique — elle s'adresse à tout public souhaitant développer ses compétences sociales dans un cadre safe, sans jugement.

---

## 🏗️ Architecture

```
quiz-dans-ta-bulle/
│
├── app.py                      # Application Streamlit principale
├── requirements.txt
│
├── data/
│   └── scenarios.json          # Base locale des 50 scénarios initiaux
│
├── assets/
│   └── images/                 # Images DALL-E 3 (générées one-shot)
│       ├── scenario_001.png
│       └── ...
│
├── utils/
│   ├── mistral_client.py       # Prompts + appels API Mistral
│   ├── scenario_loader.py      # Chargement et navigation scénarios
│   └── supabase_client.py      # CRUD Supabase
│
└── scripts/
    ├── generate_images.py      # Génération one-shot images DALL-E
    ├── generate_missing_images.py  # Mise à jour hebdo images manquantes
    └── init_supabase.py        # Population initiale Supabase
```

---

## 🛠️ Stack & choix techniques

| Composant | Technologie | Justification |
|---|---|---|
| **Interface** | Streamlit | Déploiement rapide, adapté aux apps data/AI |
| **LLM chat** | Mistral AI `mistral-small-latest` | Modèle français, performant, API accessible |
| **Génération scénarios** | Mistral AI | JSON structuré, prompt engineering soigné |
| **Images** | DALL-E 3 (OpenAI) | Qualité et cohérence visuelle — génération one-shot |
| **Base de données** | Supabase (PostgreSQL) | Persistance des scénarios générés, JSONB pour les options |
| **Déploiement** | HuggingFace Spaces | Hébergement gratuit, intégration naturelle avec l'écosystème ML |

---

## 🤖 Prompt Engineering

Le cœur de l'application est le **prompt système de Bulle**, conçu pour :

- Accueillir toute réponse sans verdict ("bien"/"mal" bannis du vocabulaire)
- Explorer la situation avec curiosité plutôt qu'enseigner
- Maintenir un registre naturel et chaleureux (3-6 phrases max)
- Ne jamais poser plusieurs questions à la fois

```python
# Extrait du prompt système
"""
Tu es Bulle, un compagnon bienveillant et curieux...
Les mots "bien", "mal", "correct" sont bannis de ton vocabulaire.
Tu n'es pas là pour enseigner, tu es là pour réfléchir ensemble. 🫧
"""
```

---

## 🗄️ Modèle de données Supabase

```sql
CREATE TABLE scenarios (
    id            TEXT PRIMARY KEY,
    theme         TEXT NOT NULL,
    contexte      TEXT NOT NULL,
    question      TEXT NOT NULL,
    options       JSONB NOT NULL,       -- {"A": "...", "B": "...", "C": "..."}
    bonne_reponse TEXT NOT NULL,
    commentaire   TEXT NOT NULL,
    image_prompt  TEXT,
    image_b64     TEXT,                 -- base64, NULL pour scénarios de base
    source        TEXT DEFAULT 'base', -- 'base' | 'generated'
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 🚀 Installation locale

```bash
# 1. Clone le repo
git clone https://github.com/TON_USERNAME/quiz-dans-ta-bulle.git
cd quiz-dans-ta-bulle

# 2. Installe les dépendances
pip install -r requirements.txt

# 3. Configure les variables d'environnement
cp .env.example .env
# Remplis .env avec tes clés API

# 4. Initialise Supabase (one-shot)
python scripts/init_supabase.py

# 5. Lance l'application
streamlit run app.py
```

### Variables d'environnement requises

```bash
MISTRAL_API_KEY=...     # console.mistral.ai
OPENAI_API_KEY=...      # platform.openai.com (génération images one-shot)
SUPABASE_URL=...        # Settings > API dans ton projet Supabase
SUPABASE_KEY=...        # Clé anon/public Supabase
```

---

## 📊 Contenu

- **58 scénarios** illustrés par DALL-E 3
- **7 thèmes** : École, Amitié, Famille, Vie quotidienne, Réseaux sociaux, Vie pro, Relations
- **Génération dynamique** de nouveaux scénarios via Mistral AI
- **Persistance** des scénarios générés dans Supabase

---

## 🔒 Confidentialité

Aucune réponse ni conversation n'est sauvegardée. Tout reste en session locale. Seuls les scénarios générés par l'IA (sans lien avec les utilisateurs) sont persistés dans Supabase.

---

## 👩‍💻 Auteure

**Aga** — Traductrice professionnelle (PL/EN/FR/RU) reconvertie en ML Engineer.  
Certifiée ML Engineer & AI Architect (Jedha Bootcamp).  
Passionnée par les applications de l'IA au service du lien humain et de l'inclusion.

🔗 [LinkedIn](https://linkedin.com/in/TON_PROFIL) · [HuggingFace](https://huggingface.co/TON_USERNAME) · [GitHub](https://github.com/TON_USERNAME)
