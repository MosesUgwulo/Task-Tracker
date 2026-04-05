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

The App Service is configured to pull a Docker image from ACR and connect to the PostgreSQL database. Connection details are injected as environment variables via Terraform's `app_settings`.

### Secrets

The PostgreSQL admin password is stored in a `terraform.tfvars` file which is gitignored. To set up:

```powershell
# Create terraform/terraform.tfvars with:
postgresql_password = "your-password-here"
```

### Deploy Infrastructure

```powershell
cd terraform
az login
terraform init
terraform plan
terraform apply
```

### Push Docker Image to ACR

After the infrastructure is up, build and push the container image:

Note: This is now automated via the GitHub Actions workflow

```powershell
az acr login --name TaskTrackerACR25
docker build -t task-tracker .
docker tag task-tracker tasktrackeracr25.azurecr.io/task-tracker:latest
docker push tasktrackeracr25.azurecr.io/task-tracker:latest
```

### Tear Down

```powershell
cd terraform
terraform destroy
```

## CI/CD (GitHub Actions)

The `.github/workflows/deploy-docker-image.yaml` workflow automates the Docker build and deployment process. It uses `workflow_dispatch` (manual trigger) so it can be run on demand when the Azure infrastructure is up.

The pipeline:

1. Checks out the repo
2. Authenticates with Azure using a service principal
3. Logs in to ACR
4. Builds and pushes the Docker image to ACR
5. Restarts the App Service to pull the new image

### Setup

A service principal is required for GitHub Actions to authenticate with Azure:
```powershell
az ad sp create-for-rbac --name "service-principal-name" --role contributor --scopes /subscriptions/<SUBSCRIPTION_ID> --sdk-auth
```

The JSON output looks like:
```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "..."
}
```

Save the entire JSON block as a single GitHub repository secret named `AZURE_CREDENTIALS` under Settings → Secrets and variables → Actions.

### Running the Pipeline

1. Ensure Azure infrastructure is up (`terraform apply`)
2. Go to the repo → Actions → "Deploy Docker Image" → "Run workflow"
3. The workflow builds, pushes, and deploys automatically

## Roadmap

- [x] FastAPI CRUD API with SQLite
- [x] Dockerise and swap SQLite for PostgreSQL
- [x] Deploy to Azure with Terraform
- [x] Wire up App Service to ACR and PostgreSQL
- [x] CI/CD pipeline with GitHub Actions
- [ ] Kubernetes orchestration
- [ ] Monitoring and observability