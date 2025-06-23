# ──────────────────────────────────────────────────────────────────────────────
# Dockerfile (ui/)
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy your dependencies specs & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Streamlit app
COPY . .

# Tell Streamlit to listen on the Cloud Run port and all interfaces
ENV PORT=8080
EXPOSE 8080

# Disable browser, set headless, bind to 0.0.0.0
CMD ["streamlit", "run", "app.py", \
     "--server.port", "8080", \
     "--server.address", "0.0.0.0", \
     "--server.headless", "true"]