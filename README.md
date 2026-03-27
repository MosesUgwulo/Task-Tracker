# Task-Tracker

A CRUD API built with FastAPI and PostgreSQL, containerised with Docker. Designed as the foundation for a full DevOps pipeline — Azure, Terraform, and CI/CD.

## Setup

### Docker (recommended)

```powershell
docker-compose up --build
```

This starts both the app and a PostgreSQL database. Data is persisted via a Docker volume.

To stop:

```powershell
docker-compose down
```

### Local Development

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Once running, you can use the app in two ways:

- **Frontend:** `http://127.0.0.1:8000` — a simple HTML interface for managing tasks
- **API docs:** `http://127.0.0.1:8000/docs` — interactive Swagger UI for testing endpoints directly

## Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Health check |
| POST | `/tasks` | Create a task |
| GET | `/tasks` | List tasks (paginated) |
| GET | `/tasks/{id}` | Get a single task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |


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

Delete a task:

```powershell
curl.exe -X DELETE "http://127.0.0.1:8000/tasks/1"
```

## Roadmap

- [x] Dockerise and swap SQLite for PostgreSQL
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Deploy to Azure with Terraform
- [ ] Kubernetes orchestration
- [ ] Monitoring and observability