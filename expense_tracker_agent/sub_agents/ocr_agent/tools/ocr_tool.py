# tools/ocr_tool.py
import os
import base64
import tempfile
from google.adk.tools import ToolContext
from google import genai

async def ocr_tool(inline_data: dict, tool_context: ToolContext):
    """
    Receives the inline_data part (with 'data' and 'mimeType'),
    writes it to a temp file, uploads to Gemini, runs OCR, and returns JSON.

    Args:
        inline_data (dict): Contains 'data' (base64 encoded content) and 'mimeType'.
        tool_context (ToolContext): Context for the tool execution.

    Returns:
        str: JSON string with extracted receipt fields.

    """
    # 1) pull out & decode
    b64 = inline_data.get("data")
    if not b64:
        raise ValueError("ocr_tool: no inline_data['data'] found")
    raw = base64.b64decode(b64)

    # 2) pick extension from mimeType
    mt = inline_data.get("mimeType", "application/pdf")
    ext = {
        "application/pdf": ".pdf",
        "image/png":      ".png",
        "image/jpeg":     ".jpg"
    }.get(mt, "")

    # 3) write to a temp file
    fd, path = tempfile.mkstemp(suffix=ext)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(raw)

        # 4) upload & OCR
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        uploaded = client.files.upload(file=path)
        prompt = (
            "Extract all visible receipt information (merchant, items, totals, date, etc) "
            "from this image/pdf. Respond with a structured JSON containing all fields."
        )
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[uploaded, prompt],
        )
        return resp.text

    finally:
        try:
            os.remove(path)
        except OSError:
            pass