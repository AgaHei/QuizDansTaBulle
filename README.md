# 🫧 Quiz dans ta bulle

> Application interactive d'entraînement aux compétences sociales, propulsée par Mistral AI et déployée sur HuggingFace Spaces.

## 🚀 **[➤ Essayer l'app en ligne](https://huggingface.co/spaces/AgaHei/Quiz-Dans-Ta-Bulle)** 🫧

[![HuggingFace Spaces](https://img.shields.io/badge/🤗%20HuggingFace%20Spaces-Quiz%20Dans%20Ta%20Bulle-ffcc33)](https://huggingface.co/spaces/AgaHei/Quiz-Dans-Ta-Bulle)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)](https://streamlit.io)
[![Mistral AI](https://img.shields.io/badge/Mistral%20AI-open--mistral--7b-orange)](https://mistral.ai)
[![DALL-E 3](https://img.shields.io/badge/DALL--E%203-Images-purple)](https://openai.com/dall-e-3)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green)](https://supabase.com)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://huggingface.co/spaces/AgaHei/Quiz-Dans-Ta-Bulle)

---

## 🎯 Concept

Quiz dans ta bulle propose des scénarios de la vie quotidienne (amitié, famille, travail, réseaux sociaux...) et invite l'utilisateur à explorer ses réactions sociales avec **Bulle**, un compagnon IA bienveillant.

L'application est conçue pour être inclusive — elle s'adresse à tout public souhaitant développer ses compétences sociales dans un cadre safe, sans jugement.

---

## 🏗️ Architecture

```
quiz-dans-ta-bulle/
│
├── app.py                      # Application Streamlit principale
├── requirements.txt
│
├── data/
│   └── scenarios.json          # Fallback local - 51 scénarios de base
│
├── assets/
│   └── images/                 # Images DALL-E 3 pour scénarios de base (générées une fois)
│       ├── scenario_001.png    
│       └── ...                 # + images DALL-E 3 en base64 dans Supabase (mises à jour périodiques)
│
├── utils/
│   ├── mistral_client.py       # Prompts + appels API Mistral
│   ├── scenario_loader.py      # Chargement et navigation scénarios
│   └── supabase_client.py      # CRUD Supabase
│
└── scripts/
    ├── generate_images.py      # Génération initiale images DALL-E 3  
    ├── update_missing_images.py  # Mise à jour périodique des images manquantes
    └── init_supabase.py        # Population initiale Supabase
```

---

## 🛠️ Stack & choix techniques

| Composant | Technologie | Justification |
|---|---|---|
| **Interface** | Streamlit + CSS personnalisé | Interface moderne, déploiement rapide sur HF Spaces |
| **LLM chat** | Mistral AI `open-mistral-7b` | Modèle français, performant, API stable et accessible |
| **Génération scénarios** | Mistral AI | Prompts optimisés pour JSON structuré, cohérence thématique |
| **Images** | DALL-E 3 (OpenAI) + système hybride | Scénarios de base = images locales DALL-E, nouveaux = 🫧 puis DALL-E périodique |
| **Base de données** | Supabase (PostgreSQL + RLS) | 58+ scénarios, sécurisé, performance optimisée |
| **Architecture** | Chargement optimisé | Scénarios sans images (rapide) + images à la demande (évite timeouts) |
| **Déploiement** | HuggingFace Spaces + Docker | Hébergement gratuit, CI/CD via Git, environnement containerisé |

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
-- Table optimisée pour éviter les timeouts lors du chargement
CREATE TABLE scenarios (
    id            TEXT PRIMARY KEY,
    theme         TEXT NOT NULL,
    contexte      TEXT NOT NULL,
    question      TEXT NOT NULL,
    options       JSONB NOT NULL,       -- {"A": "...", "B": "...", "C": "..."}
    bonne_reponse TEXT NOT NULL,
    commentaire   TEXT NOT NULL,
    image_b64     TEXT,                 -- base64, NULL pour scénarios de base, chargé individuellement 
    source        TEXT DEFAULT 'base', -- 'base' | 'generated'
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row Level Security (obligatoire pour sécurité)
ALTER TABLE scenarios ENABLE ROW LEVEL SECURITY;

-- Policy 1: Lecture publique (pour l'app quiz)
CREATE POLICY "Public read access" ON scenarios FOR SELECT TO public USING (true);

-- Policy 2: Écriture authentifiée uniquement  
CREATE POLICY "Authenticated write access" ON scenarios FOR ALL TO authenticated USING (true);
```

### Architecture anti-timeout ⚡

L'app charge les scénarios **sans** leurs images base64 pour éviter les timeouts Supabase :

1. **Chargement rapide** : `SELECT id, theme, contexte, question, options, bonne_reponse, commentaire` (pas `image_b64`)
2. **Images à la demande** : `image_b64` chargée individuellement quand un scénario s'affiche  
3. **Fallback JSON** : Si Supabase indisponible, 51 scénarios de base depuis fichier local

### Workflow images DALL-E 3 🎨

1. **Scénarios de base** : Images DALL-E 3 déjà générées et stockées localement
2. **Nouveaux scénarios** : Créés par Mistral → affichage avec placeholder 🫧  
3. **Mise à jour périodique** : Script DALL-E 3 génère les images manquantes → stockage base64 dans Supabase
4. **Affichage** : L'app charge d'abord les images locales, puis les images base64 de Supabase
```

---

## ✨ Fonctionnalités actuelles

### 🎮 Mode Quiz
- **58+ scénarios** avec images DALL-E 3 (locales pour scénarios de base, base64 en Supabase pour nouveaux)
- **Chargement optimisé** : scénarios rapides + images à la demande (évite timeouts Supabase)
- **Sélection par thème** ou mode aléatoire  
- **Interface responsive** avec CSS personnalisé et colonnes optimisées
- **Chat en temps réel** avec Bulle (Mistral AI open-mistral-7b)

### 🤖 Génération IA
- **Nouveaux scénarios** créés par Mistral AI (open-mistral-7b) à la demande
- **Classification automatique** des thèmes via prompt engineering
- **Persistance sécurisée** dans Supabase avec Row Level Security
- **Images DALL-E 3** : placeholder 🫧 initialement, puis mises à jour périodiques avec DALL-E 3
- **Workflow hybride** : génération Mistral → stockage → génération d'images DALL-E → mise à jour base

### 🛠️ Déploiement & Performance  
- **Production** : HuggingFace Spaces avec Docker (public, stable)
- **Développement** : GitHub repository avec CI/CD automatique
- **Base de données** : Supabase PostgreSQL avec RLS et optimisations anti-timeout
- **Images** : Système hybride (local + base64) pour performance optimale
- **Sécurité** : Aucune conversation stockée, politiques Supabase granulaires

---

## 🚀 Installation locale

```bash
# 1. Clone le repo
git clone https://github.com/AgaHei/Quiz-Dans-Ta-Bulle.git
cd Quiz-Dans-Ta-Bulle

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
# OBLIGATOIRE - API Mistral pour chat et génération scénarios
MISTRAL_API_KEY=...     # console.mistral.ai

# OBLIGATOIRE - Supabase pour charger les 58+ scénarios
SUPABASE_URL=...        # Settings > API dans ton projet Supabase
SUPABASE_KEY=...        # Clé service role (pas anon) pour RLS

# OPTIONNEL - Génération d'images DALL-E (mises à jour périodiques)
OPENAI_API_KEY=...      # platform.openai.com
```

### Configuration Supabase (importante)

1. **Activer Row Level Security** sur la table `scenarios`
2. **Créer 2 policies** :
   - Policy 1: `Public read access` (SELECT pour tous)
   - Policy 2: `Authenticated write access` (ALL pour authenticated)

---

## 📊 Contenu

- **58+ scénarios** avec images DALL-E 3 (locales + base64 progressivement mis à jour)
- **7 thèmes** : École, Amitié, Famille, Vie quotidienne, Réseaux sociaux, Vie pro, Relations
- **Génération dynamique** de nouveaux scénarios via Mistral AI (open-mistral-7b)
- **Images de qualité** : DALL-E 3 pour tous les scénarios (workflow de mise à jour périodique)
- **Architecture optimisée** : chargement rapide des scénarios + images à la demande
- **Sécurité** : Supabase RLS activée, aucune conversation stockée

---

## 🔒 Confidentialité

Aucune réponse ni conversation n'est sauvegardée. Tout reste en session locale. Seuls les scénarios générés par l'IA (sans lien avec les utilisateurs) sont persistés dans Supabase.

---

## 👩‍💻 Auteure

**Agnès** —   passionnée par les applications de l'IA au service du lien humain et de l'inclusion.

🔗 [LinkedIn](https://linkedin.com/in/TON_PROFIL) · [HuggingFace](https://huggingface.co/AgaHei) · [GitHub](https://github.com/AgaHei)
