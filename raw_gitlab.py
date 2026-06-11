import requests
from google.cloud import secretmanager


def get_gitlab_token():
    client = secretmanager.SecretManagerServiceClient()

    project_id = "<YOUR_GCP_PROJECT_ID>"  # 👈 your GCP project ID
    secret_id = "gitlab-token"

    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    response = client.access_secret_version(name=name)

    token = response.payload.data.decode("UTF-8")

    return token



def test_token():
    try:
        token = get_gitlab_token()

        url = "https://gitlab.com/api/v4/user"

        headers = {
            "PRIVATE-TOKEN": token
        }

        response = requests.get(url, headers=headers)

        return {
            "status_code": response.status_code,
            "response": response.text[:300]
        }

    except Exception as e:
        return {"error": str(e)}


def test_projects():
    try:
        token = get_gitlab_token()

        url = "https://gitlab.com/api/v4/projects?membership=true"

        headers = {
            "PRIVATE-TOKEN": token
        }

        response = requests.get(url, headers=headers)

        return {
            "status_code": response.status_code,
            "response": response.json()[:5]  # first 5 projects for readability
        }

    except Exception as e:
        return {"error": str(e)}



# Usage
#GITLAB_TOKEN = get_gitlab_token()
#print("DEBUG TOKEN:", GITLAB_TOKEN[:10])  # safe partial print


def test_gitlab_raw():
    token = get_gitlab_token()

    headers = {
        "PRIVATE-TOKEN": token
    }

    url = "https://gitlab.com/api/v4/projects/greenpark/finops-agent"

    response = requests.get(url, headers=headers)

    return {
        "status_code": response.status_code,
        "response": response.text[:300]
    }



