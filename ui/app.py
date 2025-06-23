# app.py
import os
import uuid
import base64
import re
import json
import requests

import streamlit as st
import pandas as pd

# ————— CONFIG —————
ADK_BASE = os.getenv("ADK_RUN_URL", "http://localhost:8000")
APP_NAME = "expense_tracker"
USER_ID  = "streamlit-user-1"

# ————— HELPERS —————
def ensure_session():
    if "session_id" not in st.session_state:
        sid = str(uuid.uuid4())
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

# 1) ensure session
ensure_session()
sid = st.session_state.session_id

# 2) file upload
uploaded = st.file_uploader("Choose a receipt file", type=["pdf", "jpg", "png"])
if uploaded:
    st.info("Expense Agent Processing…")

    # build payload
    b64 = base64.b64encode(uploaded.read()).decode()
    payload = {
        "appName":   APP_NAME,
        "userId":    USER_ID,
        "sessionId": sid,
        "streaming": False,  # must be False for simple JSON return
        "newMessage": {
            "role": "user",
            "parts": [
                {"text": "Process this receipt"},
                {"inlineData": {"mimeType": "application/pdf", "data": b64}}
            ]
        }
    }

    # call ADK
    result = call_adk(payload)

    # unpack either SSE list or direct dict
    if isinstance(result, list):
        state = {}
        for evt in result:
            actions = evt.get("actions", {}) or {}
            sd = actions.get("stateDelta", {}) or actions.get("state_delta", {})
            state.update(sd)
    else:
        state = result.get("output", {})

    # helper to remove ```json fences and parse
    def load_fenced_json(s: str):
        if not s:
            return None
        body = re.sub(r"^```json\n|```$", "", s).strip()
        return json.loads(body)

    # pull out each piece
    ocr_raw_dict = load_fenced_json(state.get("receipt_json", "")) or {}
    items_payload = load_fenced_json(state.get("items", ""))

    # ——— PATCH START ———
    # Normalize items into a simple Python list of dicts
    if isinstance(items_payload, dict) and "items" in items_payload:
        items_list = items_payload["items"]
    elif isinstance(items_payload, list):
        items_list = items_payload
    else:
        items_list = []
    # ——— PATCH END ———

    report_md = state.get("report", "")
    summary   = load_fenced_json(state.get("summary", ""))

    # — UI —

    st.subheader("🔍 Raw OCR JSON")
    st.json(ocr_raw_dict)

    if items_list:
        st.subheader("🧾 Parsed Receipt")
        st.write(f"**Merchant:** {ocr_raw_dict.get('merchant')}")
        st.write(f"**Date:**     {ocr_raw_dict.get('date')}")
        st.write(f"**Total:**    {ocr_raw_dict.get('total')}")

        # only group if the keys exist
        df = pd.DataFrame(items_list)
        if "category" in df.columns and "line_total" in df.columns:
            st.subheader("📊 Spend by Category")
            chart = df.groupby("category")["line_total"].sum().reset_index()
            st.bar_chart(chart.set_index("category"))
        else:
            st.warning("No category/line_total data available to chart.")

    if report_md:
        st.subheader("📑 Full Report")
        st.markdown(report_md)

    if summary:
        st.subheader("📝 Summary")
        st.json(summary)
