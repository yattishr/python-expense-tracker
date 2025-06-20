import os
import json
import uvicorn
from typing_extensions import Annotated

from fastapi import Form, UploadFile, File, Request
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from google.adk.cli.fast_api import get_fast_api_app
from google.adk.tools import ToolContext, FunctionTool
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
import google.genai.types as types

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Example session DB URL (e.g., SQLite)
SESSION_DB_URL = "sqlite:///./sessions.db"
# Example allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = True # Setting to False for testing purposes.

# Call the function to get the FastAPI app instance
# Ensure the agent directory name ('capital_agent') matches your agent folder
app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_db_url=SESSION_DB_URL,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# 🔧 Fix for multipart/form-data errors
@app.exception_handler(RequestValidationError)
async def handle_validation(request: Request, exc: RequestValidationError):
    return PlainTextResponse("Invalid multipart/form-data request", status_code=HTTP_422_UNPROCESSABLE_ENTITY)

# 🛠 Custom run_sse override
@app.post("/run_sse", include_in_schema=False)
async def custom_run_sse(
    file: Annotated[UploadFile, File(...)],
    app_name: Annotated[str, Form(...)],
    user_id: Annotated[str, Form(...)],
    session_id: Annotated[str, Form(...)],
    inputs: Annotated[str, Form(...)],
    streaming: Annotated[str, Form(...)]
):
    inputs_json = json.loads(inputs)
    blob = await file.read()

    # Save artifact in memory
    tool_ctx = ToolContext(
        artifact_service=InMemoryArtifactService(),
        session_id=session_id,
        app_name=app_name,
        user_id=user_id,
    )
    await tool_ctx.save_artifact(
        filename=file.filename,
        artifact=types.Part.from_data(data=blob, mime_type=file.content_type)
    )

    # Define a processing tool
    async def process_pdf_tool(tool_context: ToolContext):
        part = await tool_context.load_artifact(file.filename)
        data = await part.read()
        # Example: return PDF size
        return {"filename": file.filename, "size_bytes": len(data)}

    # Register and run agent with tool
    tool = FunctionTool(func=process_pdf_tool)
    runner = Runner(
        app,
        session_db_url=SESSION_DB_URL,
        artifact_service=InMemoryArtifactService()
    )
    response_stream = runner.run_sse(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        tool_context=tool_ctx,
        inputs=inputs_json,
        tools=[tool]
    )

    return StreamingResponse(response_stream, media_type="text/event-stream")

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))