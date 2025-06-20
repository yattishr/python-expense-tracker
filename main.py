import os
import json

import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from fastapi import Form, UploadFile, File, Request
from fastapi.responses import StreamingResponse, PlainTextResponse
from typing_extensions import Annotated

## additiional imports for custom multipart handling
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Example session DB URL (e.g., SQLite)
SESSION_DB_URL = "sqlite:///./sessions.db"
# Example allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = True

# Call the function to get the FastAPI app instance
# Ensure the agent directory name ('capital_agent') matches your agent folder
app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_db_url=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# --- Custom error handler for multipart/form-data validation ---
@app.exception_handler(RequestValidationError)
async def handle_form_validation(request: Request, exc: RequestValidationError):
    return PlainTextResponse(
        "Invalid multipart/form-data request",
        status_code=HTTP_422_UNPROCESSABLE_ENTITY
    )

# You can add more FastAPI routes or configurations below if needed
# Example:
# @app.get("/hello")
# async def read_root():
#     return {"Hello": "World"}

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))