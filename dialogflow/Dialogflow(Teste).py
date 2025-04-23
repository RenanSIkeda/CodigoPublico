import os
import uuid
from google.cloud import dialogflow_v2 as dialogflow
from google.api_core.exceptions import GoogleAPICallError

# --- Configuration ---
# Option 1: Set variables directly (replace with your actual values)
project_id = "your-gcp-project-id"
session_id = str(uuid.uuid4()) # Generate a unique session ID

# Option 2: Load from environment variables (Recommended)
# Make sure to set these environment variables in your system
# project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
# if not project_id:
#     raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")

# Generate a unique session ID for this run
session_id = str(uuid.uuid4())

language_code = "pt-BR"
text_to_send = "Olá"
# ---------------------

try:
    # Initialize the SessionsClient
    # The client uses Application Default Credentials (ADC) by default.
    # Ensure you've authenticated (e.g., using `gcloud auth application-default login`)
    session_client = dialogflow.SessionsClient()

    # Create the full session path
    session = session_client.session_path(project_id, session_id)
    print(f"Using Session Path: {session}") # Log the session path for debugging

    # Prepare the text input
    text_input = dialogflow.TextInput(text=text_to_send, language_code=language_code)

    # Prepare the query input
    query_input = dialogflow.QueryInput(text=text_input)

    # Send the request to detect the intent
    request = {
        "session": session,
        "query_input": query_input,
    }
    response = session_client.detect_intent(request=request)

    # Print the result
    print("=" * 20)
    print(f"Query text: {response.query_result.query_text}")
    print(
        f"Detected intent: {response.query_result.intent.display_name} "
        f"(confidence: {response.query_result.intent_detection_confidence:.2f})"
    )
    print(f"Fulfillment text: {response.query_result.fulfillment_text}")

except GoogleAPICallError as e:
    print(f"API Call Error: Failed to connect to Dialogflow. Details: {e}")
except ValueError as e:
    print(f"Configuration Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")