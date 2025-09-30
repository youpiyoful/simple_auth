# User Registration API

## Project structure

Below is the project layout and brief descriptions for key files:

```text
project-root/
│── docker-compose.yml           # Compose for local services (DB, SMTP mock, etc.)
│── Dockerfile                   # App image build
│── requirements.txt             # Python dependencies
│── README.md                    # Project README
│── architecture.png             # Simple architecture diagram
│
├── app/
│   ├── main.py                  # Entry point (FastAPI/Flask)
│   │
│   ├── api/                     # API layer (HTTP routes)
│   │   ├── __init__.py
│   │   ├── routes_user.py       # /register, /activate endpoints
│   │
│   ├── services/                # Business logic (OOP)
│   │   ├── __init__.py
│   │   ├── user_service.py      # UserService (registration, activation)
│   │   ├── models.py            # Domain models: User, ActivationCode
│   │   ├── exceptions.py        # Business exceptions
│   │
│   ├── persistence/             # External resource access
│   │   ├── __init__.py
│   │   ├── db.py                # DB connection (pool, context manager)
│   │   ├── user_repository.py   # PostgresUserRepository implementation
│   │   ├── email_api.py         # Email sending API simulation
│   │
│   ├── config.py                # Env variables (DB_URL, SMTP_URL, etc.)
│   ├── di.py                    # Dependency wiring
│
└── tests/
    ├── __init__.py
    ├── test_api.py              # Integration tests (routes)
    ├── test_services.py         # Unit tests (UserService)
    ├── test_repository.py       # DB tests (if needed)
```


"The project runs directly using the provided .env file for convenience and to avoid requiring reviewers to copy dev.example. However, as a best practice, if you want to change the configuration, you can copy .env.example and adapt it."

Copy the environment file:
```bash
cp .env.example .env
```