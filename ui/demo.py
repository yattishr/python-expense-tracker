# app.py
import os
import uuid
import base64
import re
import json
import io

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
        url = f"{ADK_BASE}/apps/{APP_NAME}/users/{USER_ID}/sessions/{sid}"
        r = requests.post(url)
        if not r.ok:
            st.error(f"Could not create session: {r.text}")
            st.stop()
        st.session_state.session_id = sid

def call_adk(payload):
    url = f"{ADK_BASE}/run"
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()

def load_fenced_json(s: str):
    """Strip ```json fences and parse JSON."""
    if not isinstance(s, str) or not s.strip():
        return None
    body = re.sub(r"^```json\n|```$", "", s).strip()
    return json.loads(body)

# ————— STREAMLIT UI —————
st.set_page_config(page_title="Expense Pilot", layout="wide")
st.title("🚀 Expense Pilot")

# 1) ensure session
ensure_session()
sid = st.session_state.session_id

# 2) file uploader
uploaded = st.file_uploader("Choose a receipt file", type=["pdf","jpg","png"])
if uploaded:
    st.info("Processing…")

    # build payload
    data_b64 = base64.b64encode(uploaded.read()).decode()
    payload = {
        "appName":   APP_NAME,
        "userId":    USER_ID,
        "sessionId": sid,
        "streaming": False,
        "newMessage": {
            "role": "user",
            "parts": [
                {"text": "Process this receipt"},
                {"inlineData": {"mimeType": uploaded.type, "data": data_b64}}
            ]
        }
    }

    # call ADK
    result = call_adk(payload)

    # unpack stateDelta events vs direct output
    if isinstance(result, list):
        state = {}
        for evt in result:
            act = evt.get("actions", {}) or {}
            sd  = act.get("stateDelta", {}) or act.get("state_delta", {})
            state.update(sd)
    else:
        state = result.get("output", {})

    # — parse out receipt_json, items, report wrapper —
    ocr_raw   = load_fenced_json(state.get("receipt_json", "")) or {}
    items_blob = load_fenced_json(state.get("items", ""))

    # normalize items list
    if isinstance(items_blob, dict) and "items" in items_blob:
        items = items_blob["items"]
    elif isinstance(items_blob, list):
        items = items_blob
    else:
        items = []

    # parse the ADK “report” JSON wrapper
    report_wrapper = {}
    raw_report = state.get("report", "")
    if raw_report:
        try:
            report_wrapper = json.loads(raw_report)
        except json.JSONDecodeError:
            # maybe fenced
            report_wrapper = load_fenced_json(raw_report) or {}

    summary_md = report_wrapper.get("summary_markdown", "")
    csv_data   = report_wrapper.get("csv_data", "")

    # ——— Render UI ———

    # Raw OCR JSON
    st.subheader("🔍 Raw OCR JSON")
    st.json(ocr_raw)

    # Parsed line items
    if items:
        st.subheader("🧾 Parsed Receipt")
        st.write(f"**Merchant:** {ocr_raw.get('merchant', '—')}")
        st.write(f"**Date:**     {ocr_raw.get('date',     '—')}")
        st.write(f"**Total:**    {ocr_raw.get('total',    '—')}")

        df = pd.DataFrame(items)
        if {"category","line_total"}.issubset(df.columns):
            st.subheader("📊 Spend by Category")
            cat_sum = df.groupby("category")["line_total"].sum().reset_index()
            st.bar_chart(cat_sum.set_index("category"))
        else:
            st.warning("No category/line_total data available for charting.")

    # ——— Full Report ———
    if summary_md:
        # Pull KPIs via simple regex from the markdown
        total_m = re.search(r"Total Spend.*?R ([\d,\.]+)", summary_md)
        count_m = re.search(r"Number of Receipts Processed.*?(\d+)", summary_md)
        date_m  = re.search(r"Receipt Date:\s*([\d\-]+)", summary_md)
        vendor_m= re.search(r"Vendor:\s*(.+)", summary_md)

        cols = st.columns(4)
        if total_m:   cols[0].metric("💰 Total Spend", f"R {total_m.group(1)}")
        if count_m:   cols[1].metric("📄 Receipts", count_m.group(1))
        if date_m:    cols[2].metric("🗓️ Date", date_m.group(1))
        if vendor_m:  cols[3].metric("🏬 Vendor", vendor_m.group(1).strip())

        with st.expander("📑 View Full Report", expanded=False):
            st.markdown(summary_md)

    # ——— CSV Detail Table ———
    if csv_data:
        st.subheader("📋 Line-Item Detail")
        df_csv = pd.read_csv(io.StringIO(csv_data))
        st.dataframe(df_csv, use_container_width=True)
        st.download_button(
            "⬇️ Download CSV",
            data=csv_data,
            file_name="expense_report.csv",
            mime="text/csv",
        )
