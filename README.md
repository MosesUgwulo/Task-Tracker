# Task-Tracker

A CRUD API built with FastAPI and SQLite, designed as the foundation for a full DevOps pipeline — Docker, Azure, Terraform, and CI/CD.

## Setup

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

## Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Health check |
| POST | `/tasks` | Create a task |
| GET | `/tasks` | List tasks (paginated) |
| GET | `/tasks/{id}` | Get a single task |
| PUT | `/tasks/{id}` | Update a task |


## Example Usage (PowerShell)

Create a task:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/tasks" `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Write docs\",\"description\":\"Add API examples\",\"status\":\"todo\"}'
```

List tasks:

```powershell
curl.exe "http://127.0.0.1:8000/tasks?limit=50&offset=0"
```

Get a single task:

```powershell
curl.exe "http://127.0.0.1:8000/tasks/1"
```

Update a task:

```powershell
curl.exe -X PUT "http://127.0.0.1:8000/tasks/1" `
  -H "Content-Type: application/json" `
  -d '{\"status\":\"done\"}'
```

## Roadmap

- [ ] Dockerise and swap SQLite for PostgreSQL
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Deploy to Azure with Terraform
- [ ] Monitoring and observability