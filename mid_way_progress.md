# What the backend does so far:

1.  **Initializes a FastAPI Server:** Sets up a web API framework for handling requests.
2.  **Integrates with Google Gemini LLM:** Configures and connects to the Gemini 1.5 Flash model for AI-powered text analysis.
3.  **Manages Dynamic Prompt Selection:** Stores various legal analysis prompts (e.g., for risk identification, jargon simplification, detailed analysis) and selects the appropriate one based on the `prompt_type` provided in the request.
4.  **Performs Text Analysis:**
    * Receives raw legal text and a specified analysis `prompt_type`.
    * Sends the text to the LLM with the selected prompt.
    * Parses the LLM's JSON response and validates it against predefined data structures (Pydantic models) specific to the analysis type.
    * Returns the structured legal analysis results.
5.  **Handles Document Uploads:**
    * Accepts PDF and DOCX files.
    * Extracts plain text content from these documents.
    * Submits the extracted text for `detailed_analysis` by default to the LLM.
    * Returns the comprehensive legal analysis of the document content.
6.  **Provides Interactive Documentation:** Automatically generates a Swagger UI (`/docs`) for easy testing and exploration of all API endpoints directly in a web browser.

# What I want the frontend to do:

A large text area for users to paste legal text.

A dropdown or radio buttons to select the prompt_type (e.g., "Detailed Analysis", "Risk Identification", "Jargon Simplification").

A button to trigger the analysis (which calls your /analyze-document-text endpoint).

A file upload input for PDF/DOCX files, with a button to trigger analysis (calling /upload-and-analyze).

A clear area to display the JSON output you receive from the backend. You can just pretty-print the JSON initially, or extract and display a few key fields.

Basic display of results: For the detailed analysis, displaying the raw JSON in a readable format (e.g., inside a <pre> tag or using a JSON viewer library) is perfectly acceptable for a hackathon MVP.
