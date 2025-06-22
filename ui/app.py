# app.py
import os, uuid, base64, requests
import streamlit as st

# ————— CONFIG —————
ADK_BASE    = os.getenv("ADK_RUN_URL", "http://localhost:8000")  
APP_NAME    = "expense_tracker"
USER_ID     = "streamlit-user-1"

# ————— HELPERS —————
def ensure_session():
    if "session_id" not in st.session_state:
        # 1) pick a new UUID
        sid = str(uuid.uuid4())
        # 2) fire the create-session endpoint
        create_url = f"{ADK_BASE}/apps/{APP_NAME}/users/{USER_ID}/sessions/{sid}"
        resp = requests.post(create_url)
        if not resp.ok:
            st.error(f"Failed to create session: {resp.text}")
            st.stop()
        st.session_state.session_id = sid

def call_adk(payload):
    run_url = f"{ADK_BASE}/run"
    return requests.post(run_url, json=payload).json()

# ————— STREAMLIT UI —————
st.set_page_config(page_title="Expense Pilot", layout="wide")
st.title("🚀 Expense Pilot")

# ensure we’ve got a valid session before any run
ensure_session()
sid = st.session_state.session_id

uploaded = st.file_uploader("Choose a receipt file", type=["pdf","jpg","png"])
if uploaded:
    st.info("Processing…")

    data = base64.b64encode(uploaded.read()).decode()
    payload = {
        "appName":   APP_NAME,
        "userId":    USER_ID,
        "sessionId": sid,
        "streaming": False,
        "newMessage": {
            "role": "user",
            "parts": [
                {"text": "Process this receipt"},
                {
                    "inlineData": {
                        "mimeType": "application/pdf",
                        "data":     data
                    }
                }
            ]
        }
    }
    result = call_adk(payload)

    # show the JSON and parsed fields…
    st.subheader("🔍 Raw JSON")
    st.json(result.get("output", {}).get("expense_result") or result)

    # …and your nicer summary/chart as before
    if "output" in result and "expense_result" in result["output"]:
        receipt = result["output"]["expense_result"]
        st.subheader("🧾 Parsed Receipt")
        st.write(f"**Merchant:** {receipt.get('merchant_name')}")
        st.write(f"**Date:** {receipt.get('transaction_date')}")
        st.write(f"**Total:** {receipt.get('total')} {receipt.get('currency')}")

        st.subheader("📊 Spend by Category")
        import pandas as pd
        df = pd.DataFrame(receipt["items"])
        chart = df.groupby("category")["line_total"].sum().reset_index()
        st.bar_chart(chart.set_index("category"))
