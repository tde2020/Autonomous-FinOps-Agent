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

### Google Cloud Configuration

Before running the application, update the GCP project ID in `raw_gitlab.py`:

```python
project_id = "YOUR_GCP_PROJECT_ID"
```

Replace this value with your Google Cloud project ID.

The application uses this project to retrieve the GitLab token from Google Secret Manager.


## GitLab Setup

Create a GitLab personal access token with `api` scope.

The app currently uses this project ID:

```python
GITLAB_PROJECT_ID = "my-gitlab-project-id"
```

Update it in `main.py` if you use another repo.


## Agent Configuration

The Gemini agent is implemented in `agent.py`.

Before running the agent, update the following configuration values:

```python
# Gemini API key from Google AI Studio
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

# Deployed Cloud Run API URL
FINOPS_API = "https://YOUR_CLOUD_RUN_URL"
```

### Step 1: Create a Gemini API Key

1. Open Google AI Studio.
2. Generate a Gemini API key.
3. Replace:

```python
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

with your own API key.

### Step 2: Deploy the FinOps API

Deploy the FastAPI backend to Google Cloud Run.

After deployment, Cloud Run will provide a service URL similar to:

```text
https://finops-agent-xxxxxxxxxx-ew.a.run.app
```

Replace:

```python
FINOPS_API = "https://YOUR_CLOUD_RUN_URL"
```

with your deployed endpoint.

### Step 3: Run the Agent

```bash
python agent.py
```

The agent will:

1. Retrieve cloud cost analysis from the FinOps API.
2. Analyze anomalies using Gemini.
3. Generate recommendations.
4. Create actionable GitLab remediation tickets through the deployed API.

### Example Workflow

```text
Gemini Agent
      ↓
Cloud Run FinOps API
      ↓
Analyze Billing Data
      ↓
Detect Anomalies
      ↓
Generate Recommendations
      ↓
Create GitLab Issue
```

## Devpost Summary

Autonomous FinOps Agent closes the loop between cloud cost visibility and engineering action. Instead of only reporting spend anomalies, it detects issues, explains business impact, and creates actionable GitLab tickets for teams to fix them.

## Disclaimer

This project uses mock GCP billing data for hackathon demonstration purposes.
