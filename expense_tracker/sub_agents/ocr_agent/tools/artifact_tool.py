# tools/artifact_tool.py

from google.adk.agents.callback_context import CallbackContext
from google.adk.artifacts import InMemoryArtifactService
import google.genai.types as types
import google.genai.types as types

async def artifact_tool(context: CallbackContext, file_bytes: bytes, mime_type: str = "application/pdf", filename: str = "output.pdf"):
    """
    Saves file bytes as an artifact using ADK's artifact service.

    Args:
        context (CallbackContext): ADK context (passed automatically if used as a tool).
        file_bytes (bytes): The binary data to save.
        mime_type (str): The file's MIME type (default is PDF).
        filename (str): The name to use for the saved artifact.

    Returns:
        dict: { "artifact_uri": "...", "version": ... }
    """
    try:
        artifact = types.Part.from_data(
            data=file_bytes,
            mime_type=mime_type
        )
        version = await context.save_artifact(filename=filename, artifact=artifact)
        uri = f"artifacts://{filename}@{version}"
        print(f"Saved artifact {filename} (version {version}) at {uri}")
        return {"artifact_uri": uri, "version": version}
    except Exception as e:
        print(f"Artifact save failed: {e}")
        return {"error": str(e)}

async def save_pdf_as_artifact(context: CallbackContext,file_bytes, filename, mime_type="application/pdf"):
    artifact = types.Part.from_data(
        data=file_bytes,
        mime_type=mime_type
    )
    print(f"Saving artifact {artifact} with MIME type {mime_type}")
    # Default storage (GCS) will be used; supply project, bucket if needed
    # artifact_service = ArtifactService()
    version = await context.save_artifact(filename=filename, artifact=artifact)
    artifact_uri = f"artifacts://{filename}@{version}"
    return artifact_uri