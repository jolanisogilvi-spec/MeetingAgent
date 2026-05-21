# MeetingAgent Backend

FastAPI + SQLAlchemy + SQLite.

## Run

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/api/health` to verify.
