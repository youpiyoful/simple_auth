# Architecture Dependency Injection (DI) - Simple Auth

## 🏗️ Vue d'ensemble

L'architecture DI professionnelle sépare clairement les responsabilités en plusieurs couches :

```
src/di/
├── __init__.py          # Exports publics du module
├── container.py         # Container principal d'injection
└── providers.py         # Providers par domaine métier

src/api/
└── deps.py             # Adapteurs FastAPI/HTTP uniquement

src/config/
└── settings.py         # Configuration centralisée
```

## 📋 Composants

### 1. **Providers** (`src/di/providers.py`)
Organisent les dépendances par domaine :

- **RepositoryProvider** : Couche de persistance
- **ServiceProvider** : Couche métier
- **InfrastructureProvider** : Services externes (email, etc.)

### 2. **Container** (`src/di/container.py`)
Orchestre tous les providers et fournit l'accès unifié :

```python
from src.di import get_container

container = get_container()
user_service = container.user_service()
```

### 3. **FastAPI Deps** (`src/api/deps.py`)
Adaptateurs pour l'intégration FastAPI :

```python
from src.api.deps import get_user_service, get_current_user

@router.get("/me")
def get_user_info(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}
```

## ✅ Avantages

### **Séparation claire des responsabilités**
- **Business Logic** : `src/di/` - Indépendant de FastAPI
- **HTTP Layer** : `src/api/deps.py` - Spécifique à FastAPI

### **Testabilité maximale**
```python
# Tests unitaires - pas de FastAPI
def test_user_service():
    container = create_test_container()
    service = container.user_service()
    # Test pure business logic...

# Tests d'intégration - avec FastAPI
def test_api_endpoint(client):
    response = client.post("/api/register", json={"email": "...", "password": "..."})
    # Test HTTP behavior...
```

### **Configuration centralisée**
```python
# Environment variables -> Settings
settings = get_settings()
container = AppContainer(use_mock_email=settings.use_mock_email)
```

### **Singleton garanti**
```python
# Toujours la même instance par container
service1 = container.user_service()
service2 = container.user_service()
assert service1 is service2  # True
```

## 🔧 Utilisation

### **Dans les routes FastAPI**
```python
from src.api.deps import get_user_service

@router.post("/register")
def register(
    request: RegisterRequest,
    user_service: UserService = Depends(get_user_service)
):
    return user_service.register(request.email, request.password)
```

### **Dans les tests**
```python
from src.di.container import create_test_container

def test_register_user():
    container = create_test_container()
    service = container.user_service()
    user = service.register("test@example.com", "password")
    assert user.email == "test@example.com"
```

### **Dans un CLI ou worker**
```python
from src.di import get_container

def cleanup_expired_codes():
    container = get_container()
    activation_repo = container.activation_code_repository()
    count = activation_repo.cleanup_expired()
    print(f"Cleaned {count} expired codes")
```

## 🎯 Patterns Utilisés

### **Provider Pattern**
Chaque provider encapsule la création d'un domaine spécifique.

### **Singleton Pattern**
`SingletonProvider` garantit une seule instance par container.

### **Factory Pattern**
Méthodes `_create_*()` dans les providers.

### **Adapter Pattern**
`src/api/deps.py` adapte la DI pour FastAPI.

## 🔄 Lifecycle

1. **Startup** : `get_container()` crée l'instance globale
2. **Runtime** : FastAPI utilise `Depends()` pour injecter
3. **Testing** : `create_test_container()` pour l'isolation
4. **Cleanup** : `container.cleanup_resources()` si nécessaire

## 📦 Extensions futures

### **Database Provider**
```python
class DatabaseProvider:
    def get_connection(self) -> Connection:
        return create_connection(get_settings().database_settings.url)
```

### **Cache Provider**
```python
class CacheProvider:
    def get_redis_client(self) -> Redis:
        return Redis(host=get_settings().redis_host)
```

### **External APIs Provider**
```python
class ExternalAPIProvider:
    def get_payment_client(self) -> PaymentClient:
        return PaymentClient(api_key=get_settings().payment_api_key)
```

Cette architecture DI professionnelle garantit un code maintenable, testable et extensible ! 🚀
