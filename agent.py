import requests
import json
from google import genai

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
# 🔑 Replace with your actual key from AI Studio
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

# 🌐 Your deployed Cloud Run API URL
FINOPS_API = "https://YOUR_CLOUD_RUN_URL"

# 🤖 The specific model version available in your project
MODEL_ID = "gemini-2.5-flash"

# ==========================================
# 🧠 TOOL DEFINITION
# ==========================================
def get_finops_report():
    try:
        print(f"📡 Connecting to FinOps API...")
        response = requests.get(FINOPS_API, timeout=30)
        response.raise_for_status() 
        
        full_data = response.json()
        
        # --- FIX: Only send the important parts to Gemini ---
        # This keeps the prompt small and fast.
        filtered_data = {
            "anomalies_found": full_data.get("anomalies_found", [])[:10], # Top 10 only
            "recommendations": full_data.get("recommendations", [])[:10]
        }
        
        print(f"✅ Data retrieved. Sending {len(filtered_data['anomalies_found'])} anomalies to Gemini.")
        return filtered_data
        
    except Exception as err:
        return {"error": str(err)}

# ==========================================
# 🤖 AGENT LOGIC
# ==========================================
def run_agent(user_input):
    client = genai.Client(api_key=GEMINI_API_KEY)

    print(f"\n💬 User Input: {user_input}")
    print("🤔 Gemini is thinking...")

    # --- STEP 1: INITIAL REASONING ---
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"""
            You are a FinOps AI agent. 
            User request: {user_input}
            
            Tools available:
            - get_finops_report(): Returns a JSON of billing anomalies and optimization suggestions.
            
            Instructions:
            1. If you need cost data to answer the user, respond with exactly: CALL_TOOL
            2. Otherwise, answer the user directly.
            """
        )
    except Exception as e:
        return f"❌ Gemini Error (Initial): {e}"

    decision = response.text.strip()

    # --- STEP 2: TOOL EXECUTION ---
    if "CALL_TOOL" in decision:
        tool_data = get_finops_report()

        if "error" in tool_data:
            return f"❌ Tool Error: {tool_data['error']}"

        # --- STEP 3: FINAL SYNTHESIS ---
        print("📝 Synthesizing results...")
        try:
            final_response = client.models.generate_content(
                model=MODEL_ID,
                contents=f"""
                You are a FinOps expert. Below is the cost analysis data retrieved from the system:
                
                DATA:
                {json.dumps(tool_data, indent=2)}
                
                USER ORIGINAL REQUEST:
                {user_input}
                
                YOUR TASK:
                - Summarize the anomalies found.
                - Explain the recommended actions clearly.
                - Mention the estimated savings if available.
                - Use a professional, insightful tone.
                """
            )
            return final_response.text
        except Exception as e:
            return f"❌ Gemini Error (Synthesis): {e}"

    else:
        # If Gemini didn't think it needed a tool, return its direct response
        return decision

# ==========================================
# ▶️ RUN AGENT
# ==========================================
if __name__ == "__main__":
    query = "Analyze my cloud cost and suggest optimizations"
    result = run_agent(query)

    print("\n" + "="*30)
    print("💰 FINOPS AGENT OUTPUT")
    print("="*30)
    print(result)
    print("="*30 + "\n")
