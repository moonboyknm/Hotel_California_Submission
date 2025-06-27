from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from pydantic import BaseModel, ValidationError # Import ValidationError
import re
import os
from typing import List, Dict, Any, Union # Import Union
import logging
import io # Added for file handling
import google.generativeai as genai
import json # JSON responses from LLM
from PyPDF2 import PdfReader # For PDF processing
import docx # For DOCX processing

# Import PROMPT_TEMPLATES from the new prompts.py file
from prompts import PROMPT_TEMPLATES

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
LLM_API_KEY = os.getenv("LLM_API_KEY", "YOUR_LLM_API_KEY_HERE")
LLM_MODEL_NAME = "gemini-1.5-flash"

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Legal Document Risk Analysis Backend",
    description="Processes legal documents, interacts with LLMs for risk analysis, and structures data for frontend visualization.",
    version="1.0.0"
)

# --- Models for Request and Response ---

# UPDATED: DocumentText now includes prompt_type
class DocumentText(BaseModel):
    text: str
    prompt_type: str = "risk_identification" # Default value

# This model matches the original 'risk_identification' output structure
class RiskAnalysisResult(BaseModel):
    risk_level: str
    simplified_explanation: str
    inter_clause_dependencies: List[Dict[str, str]]

# NEW: This model matches the 'detailed_analysis' output structure
class DetailedAnalysisResult(BaseModel):
    risk_level: str
    simplified_explanation: str
    inter_clause_dependencies: List[Dict[str, str]]
    vague_terms: List[Dict[str, str]]
    biased_language: List[Dict[str, str]]
    red_flags: List[Dict[str, str]]
    compounding_risks: List[Dict[str, Any]]
    structural_elements: List[Dict[str, str]]
    external_references: List[Dict[str, str]]
    exception_clauses: List[Dict[str, str]]
    jurisdictional_risks: List[Dict[str, Any]] # Adjusted to Any for internal dict values

# The main response model for /analyze-document-text endpoint will be Dict[str, Any]
# to allow for dynamic JSON outputs based on prompt_type.
# Specific validation will happen inside the endpoint logic.
# You could also use Union[RiskAnalysisResult, DetailedAnalysisResult, ... etc.]
# if the output structures are somewhat distinct but manageable within a single union.

# --- LLM and Prompt Configuration ---
genai.configure(api_key=LLM_API_KEY)
model = genai.GenerativeModel(LLM_MODEL_NAME)

# --- Helper Function for LLM Interaction ---
async def generate_llm_response(prompt_template_str: str, chunk: str, **kwargs) -> str:
    """
    Generates a response from the LLM based on a prompt template and a text chunk.
    Handles placeholder replacement and ensures JSON response mime type.
    """
    formatted_prompt = prompt_template_str.replace("{{chunk}}", chunk)

    # Handle other specific placeholders if the chosen prompt uses them
    for key, value in kwargs.items():
        placeholder = f"{{{{{key}}}}}"
        formatted_prompt = formatted_prompt.replace(placeholder, value)

    try:
        response = await model.generate_content_async(
            formatted_prompt,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        return response.text
    except Exception as e:
        logger.error(f"LLM generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {e}")

# --- API Endpoints ---

# UPDATED: response_model is now Dict[str, Any] for flexibility
@app.post("/analyze-document-text", response_model=Dict[str, Any])
async def analyze_document_text(doc_text: DocumentText):
    """
    Analyzes provided legal text based on the specified prompt type.
    """
    logger.info(f"Received request for text analysis. Prompt type: {doc_text.prompt_type}, Text length: {len(doc_text.text)}")

    if doc_text.prompt_type not in PROMPT_TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Invalid prompt_type: '{doc_text.prompt_type}'. Available types are: {', '.join(PROMPT_TEMPLATES.keys())}")

    # Use the first prompt in the selected category.
    # For more granular control, you might need an index or sub-type in the future.
    prompt_template_str = PROMPT_TEMPLATES[doc_text.prompt_type][0]

    try:
        # Pass the text to the LLM helper.
        # For prompts requiring more specific parameters (e.g., clause_a_text),
        # you would need to add them to DocumentText model and pass them here.
        # For 'detailed_analysis', only 'chunk' (doc_text.text) is used.
        llm_output = await generate_llm_response(prompt_template_str, doc_text.text)
        logger.info(f"LLM raw output (first 500 chars): {llm_output[:500]}...")

        parsed_llm_output = json.loads(llm_output)

        # Validate and return the output based on prompt_type
        if doc_text.prompt_type == "detailed_analysis":
            try:
                # Validate against the comprehensive DetailedAnalysisResult model
                validated_output = DetailedAnalysisResult(**parsed_llm_output)
                return validated_output.dict()
            except ValidationError as e:
                logger.error(f"Pydantic validation error for 'detailed_analysis' output: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"LLM output for 'detailed_analysis' failed validation: {e.errors()}")
        elif doc_text.prompt_type == "risk_identification":
            try:
                # Validate against the simpler RiskAnalysisResult model
                validated_output = RiskAnalysisResult(**parsed_llm_output)
                # You might want to add 'original_text_snippet' and 'color_code' here
                # if you intend for all outputs to conform to a similar 'FullAnalysisResponse' structure.
                # For now, it returns the direct RiskAnalysisResult dict.
                return validated_output.dict()
            except ValidationError as e:
                logger.error(f"Pydantic validation error for 'risk_identification' output: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"LLM output for 'risk_identification' failed validation: {e.errors()}")
        # Add similar elif blocks for other prompt types (e.g., 'jargon_simplification', 'overall_summary')
        # if they have specific Pydantic models or require custom processing.
        else:
            # For other prompt types, if no specific Pydantic model is defined,
            # return the raw parsed JSON.
            logger.info(f"Returning raw JSON for prompt_type: {doc_text.prompt_type}")
            return parsed_llm_output

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error from LLM. Raw LLM output: {llm_output}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LLM did not return valid JSON: {e}")
    except HTTPException as e:
        # Re-raise FastAPI HTTPExceptions directly
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred during analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

# UPDATED: response_model is now Dict[str, Any] for consistency with /analyze-document-text
@app.post("/upload-and-analyze", response_model=Dict[str, Any])
async def upload_and_analyze_document(file: UploadFile = File(...)):
    """
    Receives a document file (PDF or DOCX), extracts text, and performs analysis.
    Defaults to 'detailed_analysis' for file uploads.
    """
    extracted_text = ""
    try:
        file_content = await file.read()
        if file.filename.endswith(".pdf"):
            logger.info(f"Processing PDF file: {file.filename}")
            reader = PdfReader(io.BytesIO(file_content))
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n" # Use \n for newline
        elif file.filename.endswith(".docx"):
            logger.info(f"Processing DOCX file: {file.filename}")
            document = docx.Document(io.BytesIO(file_content))
            for paragraph in document.paragraphs:
                extracted_text += paragraph.text + "\n" # Use \n for newline
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or DOCX.")

        # For file uploads, automatically use the 'detailed_analysis' prompt type.
        # You could add a query parameter to allow the user to select this from the UI/request.
        document_for_analysis = DocumentText(text=extracted_text, prompt_type="detailed_analysis")
        return await analyze_document_text(document_for_analysis)

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")