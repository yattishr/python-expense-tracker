#!/bin/bash
APP_NAME="expense_tracker"
USER_ID="test_user"
SESSION_ID="test_file_upload_session-$(date +%s)"
FILE_PATH="C:/Users/LENOVO/Postman/files/receipt.pdf" # Ensure this path is correct for your bash environment (e.g., /c/Users/LENOVO/Postman/files/receipt.pdf in Git Bash)
FILE_KEY="file" # This will be the key in the inputs JSON referencing the artifact

# Create a new session
echo "Creating a new session..."
curl -X POST "http://localhost:8000/apps/$APP_NAME/users/$USER_ID/sessions/$SESSION_ID" \
     -H "Content-Type: application/json" \
     -d "{}" | jq .

echo "Sleeping for 2 seconds to ensure session creation is processed..."
sleep 2 # Brief pause between requests

# Step 1: Upload file to the artifact service
echo "Uploading file to artifact service..."
# The artifact service endpoint might be different, e.g., /apps/$APP_NAME/artifacts or just /artifacts
# The response should contain the artifact URI, e.g., in a 'uri' or 'artifact_uri' field.
ARTIFACT_RESPONSE=$(curl -s -X GET "http://localhost:8000/apps/$APP_NAME/users/$USER_ID/sessions/$SESSION_ID/artifacts" \
  -F "file=@$FILE_PATH;type=application/pdf" \
  -F "filename=$(basename "$FILE_PATH")" # It's good practice to send the original filename
)

echo "Artifact service response:"
echo "$ARTIFACT_RESPONSE" | jq .

# Extract the artifact URI from the response. Adjust the jq query based on the actual response structure.
# Assuming the URI is in a field named "uri" or "artifact_uri" at the top level of the JSON response.
ARTIFACT_URI=$(echo "$ARTIFACT_RESPONSE" | jq -r '.uri // .artifact_uri // .id') # Adjust as needed

if [ -z "$ARTIFACT_URI" ] || [ "$ARTIFACT_URI" == "null" ]; then
  echo "Failed to extract artifact URI. Exiting."
  exit 1
fi
echo "Extracted artifact URI: $ARTIFACT_URI"

# Step 2: Send message to the agent with the artifact URI
echo "Sending message to agent with artifact URI..."
# The 'inputs' JSON now contains the artifact URI.
# The agent should be configured to understand that 'file_uri' (or a similar key) points to an artifact.
INPUTS_JSON="{\"parts\":[{\"artifact_uri\":\"$ARTIFACT_URI\", \"key\":\"$FILE_KEY\"}]}" # Or your agent might expect a different structure

RESPONSE=$(curl -s -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \ # Sending JSON now, not multipart/form-data
  -d "{
        \"app_name\": \"$APP_NAME\",
        \"user_id\": \"$USER_ID\",
        \"session_id\": \"$SESSION_ID\",
        \"inputs\": $INPUTS_JSON,
        \"streaming\": false
      }"
)

echo "Full response from /run endpoint:"
echo "$RESPONSE" | jq .

# ... rest of your script