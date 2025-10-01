FROM python:3.13-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Provide a default .env by copying .env.example if .env is absent
RUN if [ ! -f .env ] && [ -f .env.example ]; then cp .env.example .env; fi

# Lancer l’app FastAPI avec uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
