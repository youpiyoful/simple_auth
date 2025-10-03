# Simple Auth API

API d'authentification simple avec workflow d'activation par email.

## 📚 Documentation

- ARCHITECTURE.md: Architecture applicative, Repository Pattern, DI, data model, endpoints, déploiement
- TESTING.md: Stratégie de tests (unitaires in-memory vs intégration PostgreSQL), commandes, bonnes pratiques
- VALIDATION.md: Conformité aux exigences du test technique

## 🎯 Fonctionnalités

- **Inscription** : Créer un compte utilisateur avec email/mot de passe
- **Activation par email** : Code à 4 chiffres envoyé par email (simulé en console)
- **Authentification Basic Auth** : Connexion sécurisée après activation
- **Architecture synchrone** : Simple et efficace pour ce cas d'usage

## 🏗️ Architecture

```
src/
├── main.py                   # Point d'entrée FastAPI
├── config/
│   └── settings.py           # Configuration application (.env, SMTP, DB...)
├── di/
│   └── container.py          # Conteneur d'injection de dépendances
├── api/
│   ├── server.py             # Configuration serveur FastAPI
│   ├── deps.py               # Dépendances FastAPI (auth, services...)
│   ├── routes/
│   │   └── user_routes.py    # Routes RESTful d'authentification
│   └── errors_handler.py     # Gestion globale des erreurs HTTP
├── services/
│   ├── models.py             # Modèles de données (User, ActivationCode...)
│   ├── user_service.py       # Logique métier (inscription, activation, auth)
│   └── exceptions.py         # Exceptions métier personnalisées
└── persistances/
    ├── db.py                 # Gestion des connexions PostgreSQL (pool)
    ├── email_client.py       # Client email (MockMailer/SMTPMailer)
    └── repositories/
        ├── interfaces.py                    # Abstractions Repository Pattern
        ├── email_repository.py             # Repository pour emails
        └── implementations/
            ├── postgresql_user_repository.py           # Implémentation PostgreSQL users
            ├── postgresql_activation_code_repository.py # Implémentation PostgreSQL codes
            └── memory/                                  # Implémentations in-memory (tests)
```

## 🚀 Démarrage

### 🎯 Mode Reviewer (Démarrage complet - Une seule commande)

**Pour tester rapidement l'API complète :**

```bash
docker compose up --build -d
```

Cette commande démarre automatiquement :
- **PostgreSQL** (base de données)
- **MailHog** (serveur SMTP de test avec interface web)
- **API FastAPI** (serveur principal)

**Services disponibles :**
- API : `http://localhost:8000`
- Documentation : `http://localhost:8000/docs`
- MailHog (emails) : `http://localhost:8025`

**📧 Configuration des emails :**
- **Par défaut** : Les codes d'activation s'affichent dans la console du conteneur API
- **Interface web** : Pour voir les emails dans MailHog (`http://localhost:8025`), décommentez les lignes MailHog dans le fichier `.env` :

```bash
# Décommenter ces lignes dans .env pour utiliser MailHog :
USE_MOCK_EMAIL=false
SMTP_HOST=smtp
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=false
```

### 🛠️ Mode Développeur (API en local + services Docker)

**Pour développer avec hot-reload, débogage et linter :**

#### 1. Démarrer les services externes
```bash
# PostgreSQL (obligatoire)
docker-compose up -d db

# MailHog (optionnel - pour tester les emails avec interface web)
docker-compose up -d smtp
```

#### 2. Démarrer l'API en mode développement

**⚠️ Important** : Activer l'environnement virtuel d'abord, sinon le script affichera une erreur.

```bash
# Méthode 1 : Avec Makefile (recommandé)
make dev

# Méthode 2 : Script direct (installe automatiquement les dépendances)
source venv/bin/activate  # Obligatoire !
python run_server.py

# Méthode 3 : Uvicorn manuel
source venv/bin/activate
pip install -r requirements.txt && pip install -r requirements-dev.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**💡 Le script `run_server.py` :**
- Vérifie automatiquement que l'environnement virtuel est activé
- Installe les dépendances automatiquement (`requirements.txt` + `requirements-dev.txt`)
- Lance l'API avec hot-reload activé

**Avantages du mode développeur :**
- ✅ Hot-reload automatique sur les changements de code
- ✅ Debugging facilité
- ✅ Logs détaillés dans le terminal
- ✅ Possibilité d'utiliser un IDE/debugger

**Configuration email en mode dev :**
- Par défaut : codes affichés dans la console
- Avec MailHog : interface web sur `http://localhost:8025`

### 3. Documentation API

- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

## 🔥 Test du workflow complet

### Option 1: Script automatisé

```bash
./run_tests.sh --integration
```

### Option 2: Tests manuels avec curl

#### 1. Inscription

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Réponse :**
```json
{"message": "User registered successfully. Check your email for activation code."}
```

**👀 Vérifiez la console du serveur pour voir le code à 4 chiffres**

#### 2. Activation

```bash
curl -X PATCH "http://localhost:8000/api/v1/users/{user_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "activation_code": "1234"
  }'
```

**Réponse :**
```json
{"message": "Account activated successfully."}
```

#### 3. Authentification (Basic Auth)

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Basic $(echo -n 'test@example.com:password123' | base64)"
```

**Réponse :**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "is_active": true
}
```

## 📋 API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/users` | Inscription utilisateur | ❌ |
| PATCH | `/api/v1/users/{id}` | Activation avec code à 4 chiffres | ❌ |
| POST | `/api/v1/users/{id}/codes` | Renvoyer le code d'activation | ❌ |
| GET | `/api/v1/users/me` | Informations utilisateur connecté | ✅ Basic Auth |
| GET | `/api/v1/health` | Status de l'API | ❌ |

## 🔧 Configuration

> Note importante sur les fichiers d'environnement
>
> - Le fichier `.env` **n'est pas versionné** (dans `.gitignore`), conformément aux bonnes pratiques.
> - Un fichier `.env.example` est fourni avec des valeurs de démonstration.
> - **Facilité pour reviewers** : Docker Compose copie automatiquement `.env.example` vers `.env` s'il est absent.
> - Ainsi `docker compose up --build -d` fonctionne out-of-the-box sans étape manuelle.
> - ⚠️ **Cette auto-copie est une facilité de test, PAS une pratique de production.**

### Email (Développement)

Par défaut, l'API utilise un `MockMailer` qui affiche les codes d'activation dans la console.

### Email (Production)

Pour utiliser un vrai serveur SMTP, modifiez `src/persistances/email_client.py` :

```python
# Remplacer la ligne:
Mailer = MockMailer

# Par:
Mailer = SMTPMailer(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your-email@gmail.com",
    password="your-app-password"
)
```

## 🛠️ Développement

### Architecture Repository Pattern

**Structure des repositories :**
```
src/persistances/repositories/
├── interfaces.py                           # Abstractions pures
└── implementations/
    ├── postgresql_*.py                     # Production (PostgreSQL)
    └── memory/                             # Tests/Demos (In-Memory)
```

**Configuration flexible :**
```python
# Production : PostgreSQL (défaut)
from src.di.container import get_container
container = get_container()  # use_postgresql=True par défaut

# Tests : In-Memory
container = AppContainer(use_postgresql=False)
```

### Dépendances de développement (formatteurs/lint)

Installe les outils de dev (formatteurs) sans les dépendances de test:

```bash
pip install -r requirements-dev.txt
```

Ou, si tu veux tout pour les tests et le formatage dans un même environnement:

```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Formater le code

```bash
# Trier les imports
isort .

# Formater le code
black .
```

### Raccourcis Makefile (optionnels)

```bash
# Préparer .env si absent
make env

# Lancer en local
make dev

# Docker
make build
make up
make down
make logs

# Tests
make test
make unit
make integration

# Formatage
make fmt
make fmt-check
```

### Hooks pre-commit (optionnel)

```bash
# Installer les hooks
pip install -r requirements-dev.txt
make hooks-install

# Vérifier/auto-corriger
make hooks-run
make hooks-autofix
```

### Structure synchrone

L'API utilise une architecture **synchrone** car :
- ✅ Plus simple pour ce cas d'usage
- ✅ Pas de complexité async inutile
- ✅ Performance suffisante pour un test
- ✅ Code plus lisible et maintenable

### **Repository Pattern avec PostgreSQL**

L'application utilise de **vraies implémentations PostgreSQL** en production :
- `PostgreSQLUserRepository` : CRUD SQL pour les utilisateurs
- `PostgreSQLActivationCodeRepository` : Gestion SQL des codes d'activation
- **Persistance réelle** : Les données survivent aux redémarrages
- **Implémentations in-memory** : Disponibles pour tests rapides
- Auto-nettoyage des codes expirés (SQL `DELETE WHERE expires_at < NOW()`)

## 🧪 Tests

L'application utilise une **architecture de tests à deux niveaux** :

### Tests Unitaires (Rapides)
```bash
# Tests in-memory ultra-rapides (~2s)
pytest -m unit
```

### Tests d'Intégration (Complets)
```bash
# Tests avec PostgreSQL (~2s)
pytest -m integration
```

### Tous les Tests
```bash
# Exécution complète
pytest

# Ou avec le script
./run_tests.sh
```

### **📊 Couverture Actuelle**
- **21 tests** au total
- **12 tests unitaires** (in-memory, logique métier)
- **9 tests d'intégration** (PostgreSQL, API complète)

Voir **[TESTING.md](TESTING.md)** pour la documentation complète de la stratégie de tests.

### **Scénarios Validés**
1. ✅ Inscription utilisateur + code d'activation
2. ✅ Activation avec codes 4 chiffres (1 minute)
3. ✅ Authentification Basic Auth
4. ✅ Gestion des erreurs et cas limites
5. ✅ Repository Pattern (PostgreSQL + in-memory)

## 📝 Notes techniques

### Basic Auth
```
Authorization: Basic <base64(email:password)>
```

### Codes d'activation
- **Format** : 4 chiffres (ex: 1234)
- **Expiration** : 1 minute
- **Unicité** : Garantie par le repository

### Sécurité
- Mots de passe hachés avec `bcrypt`
- Codes d'activation temporaires
- Validation des emails avec Pydantic
