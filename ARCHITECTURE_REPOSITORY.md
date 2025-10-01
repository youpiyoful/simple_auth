# Repository Pattern - Implémentation Simple Auth

## 🎯 Architecture Mise à Jour

Suite à la refactorisation majeure, l'application Simple Auth implémente désormais un **Repository Pattern professionnel** avec une séparation claire entre interfaces et implémentations.

## 🏗️ Structure Finale

### **Avant (Problématique)**
```
❌ Mélange interface + implémentation dans même fichier
❌ Utilisation d'implémentations in-memory en production
❌ Pas de vraie persistance PostgreSQL
```

### **Après (Solution)**
```
✅ Interfaces pures séparées des implémentations
✅ Vraies implémentations PostgreSQL en production
✅ Implémentations in-memory disponibles pour tests
✅ Configuration flexible via DI Container
```

## 📁 Organisation des Fichiers

```
src/persistances/repositories/
├── interfaces.py                           # 🔒 Contrats abstraits
└── implementations/                        # 🛠️ Implémentations concrètes
    ├── __init__.py                         # 📦 Exports
    ├── postgresql_user_repository.py       # 🐘 Production
    ├── postgresql_activation_code_repository.py
    └── memory/                             # 🧠 Tests/Démos
        ├── __init__.py
        ├── user_repository.py
        └── activation_code_repository.py
```

## 🔄 Flux d'Utilisation

### **Production (Défaut)**
```python
# 1. Container utilise PostgreSQL par défaut
container = AppContainer()  # use_postgresql=True

# 2. Services reçoivent les implémentations PostgreSQL
user_service = container.user_service()

# 3. Vraies requêtes SQL exécutées
user = user_service.register("user@example.com", "password")
# → INSERT INTO users (id, email, password_hash, ...) VALUES (...)
```

### **Tests Unitaires (Rapides)**
```python
# 1. Container configuré pour in-memory
container = AppContainer(use_postgresql=False)

# 2. Tests s'exécutent sans DB
user_service = container.user_service()

# 3. Stockage en dictionnaires Python (rapide)
user = user_service.register("test@example.com", "password")
# → self._users[user.id] = user
```

## 🛢️ Implémentations PostgreSQL

### **PostgreSQLUserRepository**
```python
def create(self, user: User) -> User:
    query = """
        INSERT INTO users (id, email, password_hash, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s) RETURNING *
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (user.id, user.email, ...))
        return User(**cursor.fetchone())
```

### **PostgreSQLActivationCodeRepository**
```python
def create(self, user_id: str) -> ActivationCode:
    query = """
        INSERT INTO activation_codes (user_id, code, created_at, expires_at)
        VALUES (%s, %s, NOW(), NOW() + INTERVAL '1 minute')
        RETURNING *
    """
    # Génération code + insertion SQL
```

## 🧪 Avantages pour les Tests

### **Tests Unitaires**
```python
# Rapides : pas de DB, stockage mémoire
def test_user_registration():
    container = AppContainer(use_postgresql=False)
    service = container.user_service()
    # Test de la logique pure, pas de la persistance
```

### **Tests d'Intégration**
```python
# Réalistes : vraie DB PostgreSQL
def test_user_flow_integration():
    container = AppContainer(use_postgresql=True)
    # Test du flux complet avec vraie persistance
```

## ⚡ Impact Performance

| Type | PostgreSQL | In-Memory |
|------|------------|-----------|
| **Vitesse** | Production réaliste | Tests ultra-rapides |
| **Persistance** | ✅ Survit redémarrage | ❌ RAM seulement |
| **Concurrence** | ✅ Multi-utilisateurs | ❌ Thread unique |
| **Transactions** | ✅ ACID compliant | ❌ Pas de rollback |

## 🎯 Conformité Test Technique

### ✅ **PostgreSQL Requis**
- Vraies implémentations SQL en production
- Schéma de base complet (users, activation_codes)
- Connexions poolées et transactions

### ✅ **Architecture Professionnelle**
- Repository Pattern avec séparation claire
- Dependency Injection configurable
- Clean Architecture respectée

### ✅ **Flexibilité et Tests**
- Basculement facile PostgreSQL ↔ In-Memory
- Tests rapides sans dépendance DB
- Mocks et stubs intégrés

---

## 🚀 Migration Effectuée

**De :** Implémentations in-memory en production (non conforme)
**Vers :** Vraies implémentations PostgreSQL + in-memory pour tests

**Résultat :** Application conforme aux spécifications du test technique avec une architecture extensible et maintenable.
