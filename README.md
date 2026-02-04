# MyBackend (FastAPI) — 简易可部署模板

This repository is a minimal FastAPI backend template intended for learning and small personal deployments. It includes user registration, login (JWT), and a protected `/me` endpoint. It uses SQLModel on top of SQLite by default.

Important notes:
- For development this project temporarily uses `pbkdf2_sha256` (pure Python) for password hashing to avoid native `bcrypt` build issues on some systems. This is secure for development and learning. See LEARNING_GUIDE.md for how to switch to `bcrypt` for production.
- The OpenAPI (Swagger) UI is available at `/docs` unless disabled via `DISABLE_DOCS=1`.

Quick start (WSL / local):
1. Clone repository and enter folder:
   git clone https://github.com/pushk3n/rear_end.git
   cd rear_end

2. Create and activate virtualenv:
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies:
   pip install -U pip
   pip install -r requirements.txt

4. Set environment variables (example):
   export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
   export DATABASE_URL="sqlite:///./data.db"
   export DISABLE_DOCS=0

5. Run the app (development):
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

6. Test endpoints:
   curl -X POST "http://127.0.0.1:8000/register" -H "Content-Type: application/json" -d '{"username":"test","password":"123456"}'
   curl -X POST "http://127.0.0.1:8000/login" -H "Content-Type: application/json" -d '{"username":"test","password":"123456"}'

How to pull the repository updates on your machine (WSL or VPS):
1. cd /path/to/rear_end
2. git pull origin main
3. If dependencies changed, re-run `pip install -r requirements.txt` inside the venv.

See LEARNING_GUIDE.md for an explained walkthrough of database basics, JWT, and the code flow.
