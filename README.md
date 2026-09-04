# PlatformActia Backend API

API Backend construite avec [FastAPI](https://fastapi.tiangolo.com/).

## 📁 Arborescence du Projet

```text
PlatformActia/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── health.py
│   │       └── router.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── tests/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## 🚀 Installation & Démarrage

### 1. Prérequis
- Python 3.10+ installed

### 2. Création de l'environnement virtuel
```bash
python -m venv venv
# Sur Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Sur Linux/macOS:
source venv/bin/activate
```

### 3. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 4. Lancement du serveur de développement
```bash
uvicorn app.main:app --reload --port 8000
```

- Documentation Swagger UI : [http://localhost:8000/docs](http://localhost:8000/docs)
- Documentation ReDoc : [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health check : [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
