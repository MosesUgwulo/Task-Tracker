# Task-Tracker

A CRUD API built with FastAPI and PostgreSQL, designed as the foundation for a full DevOps pipeline — Docker, Azure, Terraform, and CI/CD.

## Local Setup

### Run with Docker (recommended)

```powershell
docker-compose up --build
```

This starts up two containers: The FastAPI app and a PostgreSQL database. Data is persisted via a Docker volume.

To stop:

```powershell
docker-compose down
```

### Local Development (Running without Docker)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Note: Running without Docker requires a PostgreSQL instance running separately with the connection details matching the environment variables in `main.py`.

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

## Azure Infrastructure (Terraform)
 
The `terraform/` directory contains the infrastructure-as-code for deploying to Azure. Resources provisioned:
 
- Resource Group
- Azure Container Registry (ACR)
- App Service Plan (B1 Linux)
- Linux Web App (App Service for Containers)
- PostgreSQL Flexible Server + database + firewall rule
 
### Deploy
 
```powershell
cd terraform
az login
terraform init
terraform plan
terraform apply
```
 
### Tear down
 
```powershell
terraform destroy
```

## Roadmap

- [x] FastAPI CRUD API with SQLite
- [x] Dockerise and swap SQLite for PostgreSQL
- [x] Deploy to Azure with Terraform
- [ ] Wire up App Service to ACR and PostgreSQL
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Kubernetes orchestration
- [ ] Monitoring and observability