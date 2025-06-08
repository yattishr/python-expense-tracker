# tools/ocr_tool.py
import os
from google.adk.tools import ToolContext
from google import genai

def ocr_tool(image_path: str, tool_context: ToolContext):
    """
    Uploads an image or PDF and uses Gemini to extract structured receipt text.
    Returns the model’s raw response (string or JSON).
    """
    # read your key from .env or environment
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    # 1) upload
    uploaded_file = client.files.upload(file=image_path)
    
    # 2) prompt Gemini to extract structured fields
    prompt = (
        "Extract all visible receipt information (merchant, items, totals, date, etc) "
        "from this image/pdf. Respond with a structured JSON containing all fields."
    )
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[uploaded_file, prompt],
    )
    return response.text  # Or .json() if you set JSON mode later