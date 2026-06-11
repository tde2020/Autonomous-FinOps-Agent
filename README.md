# Autonomous FinOps Agent: From Cloud Analysis to Cost Actions

An AI-powered FinOps agent that detects cloud cost anomalies, recommends optimizations, and automatically creates GitLab issues for engineering follow-up.

## What it does

- Reads mock GCP billing data at SKU/project/day level
- Detects unusual cloud cost spikes
- Suggests optimization actions
- Creates GitLab issues automatically
- Provides a deployed API that Gemini can call as an agent tool

## Architecture

```text
Gemini Agent
   ↓
Cloud Run FastAPI backend
   ↓
Mock GCP billing CSV
   ↓
Anomaly detection + recommendations
   ↓
GitLab issue creation
```

## Tech Stack

- Python
- FastAPI
- Google Cloud Run
- Google Secret Manager
- GitLab API
- Gemini API
- Pandas

## Project Structure

```text
.
├── main.py
├── raw_gitlab.py
├── agent.py
├── gcp_mock_billing_data.csv
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

## API Endpoints

### Health check

```http
GET /
```

### Full FinOps report

```http
GET /full_finops_report
```

### Create GitLab ticket

```http
POST /create_ticket
```

Example body:

```json
{
  "title": "FinOps Test Ticket",
  "description": "Created from Cloud Run API",
  "priority": "high"
}
```

### Run autonomous flow

```http
GET /run_finops_agent
```

This runs:

```text
analyze costs → detect anomalies → create GitLab issues
```

## Local Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

Open:

```text
http://localhost:8080/docs
```

## Google Cloud Setup

Enable:

- Cloud Run Admin API
- Cloud Build API
- Artifact Registry API
- Secret Manager API

Create a GCP secret named:

```text
gitlab-token
```

The Cloud Run service account needs:

```text
Secret Manager Secret Accessor
```

Deploy:

```bash
gcloud run deploy finops-agent \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated
```

## GitLab Setup

Create a GitLab personal access token with `api` scope.

The app currently uses this project ID:

```python
GITLAB_PROJECT_ID = "my-gitlab-project-id"
```

Update it in `main.py` if you use another repo.

## Demo Flow

1. Open `/full_finops_report`
2. Show detected anomalies and recommendations
3. Open `/run_finops_agent`
4. Show newly created GitLab issues

## Devpost Summary

Autonomous FinOps Agent closes the loop between cloud cost visibility and engineering action. Instead of only reporting spend anomalies, it detects issues, explains business impact, and creates actionable GitLab tickets for teams to fix them.

## Disclaimer

This project uses mock GCP billing data for hackathon demonstration purposes.
