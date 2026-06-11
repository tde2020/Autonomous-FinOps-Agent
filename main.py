from fastapi import FastAPI
import pandas as pd
from typing import Optional
import os
import gitlab 

from raw_gitlab import (
    test_gitlab_raw,
    test_token,
    test_projects,
    get_gitlab_token
)


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FinOps Agent API is running. Use /docs for documentation."}

@app.get("/test_gitlab_raw")
def run_test():
    return test_gitlab_raw()

@app.get("/test_token")
def run_test_token():
    return test_token()

@app.get("/test_projects")
def run_test_projects():
    return test_projects()


# Load CSV once
df = pd.read_csv("gcp_mock_billing_data.csv")

# -------------------------
# TOOL 1: get_cloud_costs
# -------------------------
@app.get("/get_cloud_costs")

def get_cloud_costs(start_date: str, end_date: str, project_id: Optional[str] = None):
    filtered = df[
        (df["date"] >= start_date) &
        (df["date"] <= end_date)
    ]
    
    if project_id:
        filtered = filtered[filtered["project_id"] == project_id]

    return filtered.to_dict(orient="records")


# -------------------------
# TOOL 2: detect_anomalies
# -------------------------
@app.post("/detect_anomalies")
def detect_anomalies(cost_data: list):
    data = pd.DataFrame(cost_data)

    anomalies = []
    
    grouped = data.groupby("service")["cost_eur"].mean()

    for service in data["service"].unique():
        service_data = data[data["service"] == service]
        avg = grouped[service]

        for _, row in service_data.iterrows():
            if row["cost_eur"] > avg * 1.3:
                anomalies.append({
                    "service": service,
                    "date": row["date"],
                    "cost": row["cost_eur"],
                    "increase_vs_avg": round((row["cost_eur"]/avg - 1)*100, 2)
                })

    return {"anomalies": anomalies}

@app.get("/detect_anomalies_from_file")
def detect_anomalies_from_file():
    # 1. Use the existing global dataframe
    # 2. Convert it to the list format the detection logic expects
    data_list = df.to_dict(orient="records")
    
    # 3. Run the same logic you have in detect_anomalies
    return detect_anomalies(data_list)



# -------------------------
# TOOL 3: suggest_optimizations
# -------------------------
@app.post("/suggest_optimizations")
def suggest_optimizations(anomalies: dict):
    recommendations = []

    for a in anomalies.get("anomalies", []):
        if a["service"] == "Compute Engine":
            recommendations.append({
                "action": "Shut down idle instances or resize machines",
                "estimated_savings": "€1000/month",
                "confidence": 0.85
            })
        else:
            recommendations.append({
                "action": f"Optimize usage for {a['service']}",
                "estimated_savings": "€300/month",
                "confidence": 0.7
            })

    return {"recommendations": recommendations}


@app.get("/full_finops_report")
def full_finops_report():
    # Step 1: Get data from the CSV
    data_list = df.to_dict(orient="records")
    
    # Step 2: Find anomalies
    anomalies_result = detect_anomalies(data_list)
    
    # Step 3: Get suggestions based on those anomalies
    optimization_results = suggest_optimizations(anomalies_result)
    
    return {
        "anomalies_found": anomalies_result["anomalies"],
        "recommendations": optimization_results["recommendations"]
    }




# -------------------------
# TOOL 4: create_ticket (mock)
# -------------------------
#@app.post("/create_ticket")
#def create_ticket(title: str, description: str, priority: str):
#    return {
#        "status": "created",
#        "title": title,
#        "priority": priority,
#        "message": "Mock ticket created (GitLab integration later)"
#    }

from pydantic import BaseModel
import requests

class TicketRequest(BaseModel):
    title: str
    description: str
    priority: str

@app.post("/create_ticket")
def create_ticket(req: TicketRequest):
    try:
        token = get_gitlab_token()

        # replace <my-gitlan-project-id> below with the project id
        url = "https://gitlab.com/api/v4/projects/<my-gitlab-project-id>/issues" 

        headers = {
            "PRIVATE-TOKEN": token,
            "Content-Type": "application/json"
        }

        payload = {
            "title": f"[{req.priority.upper()}] {req.title}",
            "description": req.description,
            "labels": f"{req.priority},finops-anomaly"
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        return {
            "gitlab_status": response.status_code,
            "gitlab_response": response.json()
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }



# run finops agent

@app.get("/run_finops_agent")
def run_finops_agent():
    report = full_finops_report()

    anomalies = report["anomalies_found"]

    if not anomalies:
        return {
            "status": "no_action_needed",
            "message": "No anomalies found. No GitLab ticket created."
        }

    # Create ONE summary ticket only
    top_anomalies = sorted(
        anomalies,
        key=lambda x: x["increase_vs_avg"],
        reverse=True
    )[:5]

    anomaly_lines = []

    for anomaly in top_anomalies:
        anomaly_lines.append(
            f"""
### {anomaly['service']} - {anomaly.get('sku')}

- Project: {anomaly.get('project_id')}
- Date: {anomaly['date']}
- Cost: €{anomaly['cost']}
- Increase vs average: {anomaly['increase_vs_avg']}%
"""
        )

    description = f"""
# FinOps Cost Anomaly Report

The Autonomous FinOps Agent detected **{len(anomalies)} anomalies** in the mock GCP billing data.

This ticket summarizes the **top 5 highest-impact anomalies** for engineering review.

{''.join(anomaly_lines)}

## Recommended Actions

- Investigate unexpected Compute Engine, GPU, or workload spikes
- Check for idle or oversized resources
- Validate whether usage was expected
- Rightsize or shut down unused resources
- Review cost ownership by project/team

## Agent Decision

A single summary ticket was created to avoid alert fatigue and ticket spam.
"""

    ticket = create_ticket(
        TicketRequest(
            title="FinOps Cost Anomaly Summary",
            description=description,
            priority="high"
        )
    )

    return {
        "status": "ticket_created",
        "total_anomalies_detected": len(anomalies),
        "ticket_created": ticket
    }

