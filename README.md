# Simple Auth API

API d'authentification simple avec workflow d'activation par email.

## 🎯 Fonctionnalités

- **Inscription** : Créer un compte utilisateur avec email/mot de passe
- **Activation par email** : Code à 4 chiffres envoyé par email (simulé en console)
- **Authentification Basic Auth** : Connexion sécurisée après activation
- **Architecture synchrone** : Simple et efficace pour ce cas d'usage

## 🏗️ Architecture

```
src/
├── main.py                   # Point d'entrée FastAPI
├── api/
│   ├── server.py             # Configuration serveur
│   ├── routes/
│   │   └── user_routes.py    # Routes d'authentification
│   └── errors_handler.py     # Gestion des erreurs
├── services/
│   ├── models.py             # Modèles de données
│   ├── user_service.py       # Logique métier
│   └── exceptions.py         # Exceptions personnalisées
└── persistances/
    ├── email_client.py       # Client email (mock pour dev)
    └── repositories/
        ├── user_repository.py           # Repository utilisateurs
        └── activation_code_repository.py # Repository codes d'activation
```

## 🚀 Démarrage rapide

### 1. Installation des dépendances (runtime)

```bash
pip install -r requirements.txt
```

### 2. Lancement du serveur

```bash
python src/main.py
```

Le serveur démarre sur `http://localhost:8000`

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
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "motdepasse123"}'
```

**Réponse :**
```json
{"message": "User registered successfully. Check your email for activation code."}
```

**👀 Vérifiez la console du serveur pour voir le code à 4 chiffres**

#### 2. Activation

```bash
curl -X POST "http://localhost:8000/activate" \
     -H "Content-Type: application/json" \
     -d '{"activation_code": "1234"}'
```

**Réponse :**
```json
{"message": "Account activated successfully."}
```

#### 3. Authentification (Basic Auth)

```bash
curl -X GET "http://localhost:8000/me" \
     -H "Authorization: Basic dGVzdEBleGFtcGxlLmNvbTptb3RkZXBhc3NlMTIz"
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
| POST | `/register` | Inscription utilisateur | ❌ |
| POST | `/activate` | Activation avec code à 4 chiffres | ❌ |
| POST | `/resend-code` | Renvoyer le code d'activation | ❌ |
| GET | `/me` | Informations utilisateur connecté | ✅ Basic Auth |
| GET | `/health` | Status de l'API | ❌ |

## 🔧 Configuration

> Note importante sur les fichiers d'environnement
>
> - Le fichier `.env` n'est **pas** versionné. À la place, on fournit **`.env.example`** avec des valeurs de démonstration.
> - Pour faciliter les tests reviewers: le **Dockerfile copie `.env.example` vers `.env`** automatiquement si `.env` est absent. Ainsi `docker compose up` fonctionne out‑of‑the‑box.
> - En local hors Docker: crée ton `.env` avec `cp .env.example .env` et personnalise si besoin.

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

### Repositories in-memory

Les données sont stockées en mémoire pour la simplicité :
- `UserRepository` : Gestion des utilisateurs
- `ActivationCodeRepository` : Gestion des codes temporaires
- Auto-nettoyage des codes expirés

## 🧪 Tests

Exécuter la suite de tests avec couverture:

```bash
./run_tests.sh
```

Le fichier `tests/test_integration.py` teste le workflow complet :

1. ✅ Health check
2. ✅ Inscription utilisateur  
3. ✅ Activation avec code
4. ✅ Authentification Basic Auth

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