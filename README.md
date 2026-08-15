# Enterprise Knowledge Management and AI Document Search Platform

Runnable starter project for the Software Engineering Git/Docker assignment.

Features: registration/login, JWT auth, document upload, document listing, AI-style TF-IDF search, PostgreSQL, Docker Compose.

## Run
Install Docker Desktop, then run:

```bash
docker compose up --build
```

Open http://localhost:3000 and register. API docs: http://localhost:8000/docs

Stop with `docker compose down`. Remove database data with `docker compose down -v`.
