from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from pydantic import BaseModel
import re
import os
from typing import List, Dict, Any
import logging
import io # Added for file handling
import google.generativeai as genai 
import json # JSON responses from LLM

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
# You'll replace this with your actual LLM API key and model details
# For a hackathon, you might use a dummy key or environment variable
LLM_API_KEY = os.getenv("LLM_API_KEY", "YOUR_LLM_API_KEY_HERE")
LLM_MODEL_NAME = "gemini-2.5-flash" # Example model name for Google Gemini

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Legal Document Risk Analysis Backend",
    description="Processes legal documents, interacts with LLMs for risk analysis, and structures data for frontend visualization.",
    version="1.0.0"
)

# --- Models for Request and Response ---
class DocumentText(BaseModel):
    text: str

class AnalysisResult(BaseModel):
    original_text_snippet: str
    risk_level: str # e.g., "high", "medium", "low", "neutral"
    color_code: str # e.g., "#FF0000" for high, "#FFFF00" for medium
    simplified_explanation: str
    inter_clause_dependencies: List[Dict[str, str]] # e.g., [{"clause_id": "clause_X", "dependency_type": "reinforces"}]

class FullAnalysisResponse(BaseModel):
    document_title: str # You might extract this or provide a default
    total_chunks: int
    analysis_chunks: List[AnalysisResult]
    overall_summary: str

# --- Helper Functions ---

def preprocess_text(text: str) -> str:
    """Removes irrelevant elements and standardizes text format."""
    # Remove excessive whitespace, newlines, tabs
    text = re.sub(r'\s+', ' ', text).strip()
    # You might add more advanced cleaning here (e.g., removing headers/footers based on patterns)
    return text

def segment_text(text: str, max_chunk_size: int = 500) -> List[str]:
    """
    Segments the document into logical chunks based on max_chunk_size.
    Prioritizes sentence boundaries.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        # Check if adding the current sentence would exceed the max_chunk_size
        # +1 for the space after the sentence
        if len(current_chunk) + len(sentence) + (1 if current_chunk else 0) <= max_chunk_size:
            current_chunk += (sentence + " ").strip()
        else:
            if current_chunk: # Add the current chunk if it's not empty
                chunks.append(current_chunk)
            current_chunk = (sentence + " ").strip()
    if current_chunk: # Add the last chunk if it's not empty
        chunks.append(current_chunk)
    return chunks

async def call_llm_api(prompt: str, task: str) -> Dict[str, Any]:
    """
    Makes an actual LLM API call to Google Gemini.
    """
    logger.info(f"Calling LLM for task: {task} with prompt sample: {prompt[:100]}...")

    try:
        # --- Actual Google Gemini Integration ---
        genai.configure(api_key=LLM_API_KEY)
        model = genai.GenerativeModel(LLM_MODEL_NAME)

        # For tasks where you expect structured (JSON) output from the LLM,
        # it's best to explicitly ask for JSON in the prompt and then parse it.
        # Ensure your LLM model is capable of generating valid JSON.
        if task in ["risk_identification"]:
            # If you specifically prompt for JSON, ensure the LLM returns valid JSON.
            # You might use model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            # if your model supports it and you strictly want JSON.
            # For simpler text-based JSON, ensure your prompt guides the LLM clearly.
            response = await model.generate_content_async(prompt)
            response_text = response.text # Get the text response from the LLM

            try:
                # Attempt to parse the LLM's response as JSON
                parsed_response = json.loads(response_text)
                return parsed_response
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON for task {task}: {e}. Response: {response_text[:500]}", exc_info=True)
                # Fallback or raise an error if JSON parsing is critical
                raise HTTPException(status_code=500, detail=f"LLM returned invalid JSON for {task}: {response_text[:100]}...")

        elif task in ["jargon_simplification", "overall_summary"]:
            # For tasks where you expect plain text, just return the text.
            response = await model.generate_content_async(prompt)
            response_text = response.text
            if task == "jargon_simplification":
                return {"simplified_text": response_text}
            elif task == "overall_summary":
                return {"summary": response_text}
        else:
            # Fallback for any other tasks, or specific handling if needed
            response = await model.generate_content_async(prompt)
            return {"analysis": response.text}

    except Exception as e:
        logger.error(f"LLM API call failed for task {task}: {e}", exc_info=True)
        # Check for specific exceptions like API key errors, rate limits, etc.
        # Example for Google Generative AI (you might need to refine this based on actual errors):
        # if "API key not valid" in str(e):
        #     raise HTTPException(status_code=401, detail="Invalid LLM API Key.")
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {e}")

def map_risk_to_color(risk_level: str) -> str:
    """Maps risk level to a color code."""
    if risk_level.lower() == "high":
        return "#FF4D4D"  # Red
    elif risk_level.lower() == "medium":
        return "#FFA500" # Orange
    elif risk_level.lower() == "low":
        return "#FFD700"  # Gold/Yellow
    else: # Neutral
        return "#87CEEB"  # SkyBlue (or a lighter green/blue for neutral)

# --- Primary API Endpoint for Text Analysis ---
@app.post("/analyze", response_model=FullAnalysisResponse)
async def analyze_document_text(document: DocumentText): # Removed 'request: Request' if not explicitly used
    """
    Primary API endpoint to receive a legal document (plain text) and return its risk analysis.
    """
    try:
        raw_text = document.text
        logger.info(f"Received document for analysis. Length: {len(raw_text)} characters.")

        # 1. Text Preprocessing
        cleaned_text = preprocess_text(raw_text)
        text_chunks = segment_text(cleaned_text)
        logger.info(f"Document segmented into {len(text_chunks)} chunks.")

        analysis_chunks: List[AnalysisResult] = []
        overall_summary_parts: List[str] = []

        # 2. LLM Interaction for Each Chunk
        for i, chunk in enumerate(text_chunks):
            # Prompt the LLM to identify risks and provide structured output (JSON)
            risk_prompt = (
                f"Analyze the following legal text for vague language, biased terms, unfair clauses, "
                f"and potential liabilities. Based on your analysis, provide a JSON object with the following keys:\n"
                f"- 'risk_level': a string, either 'High', 'Medium', 'Low', or 'Neutral'.\n"
                f"- 'simplified_explanation': a concise, plain language explanation of the identified risks or key points.\n"
                f"- 'inter_clause_dependencies': a list of objects, where each object has 'clause_id' (string) and 'dependency_type' (string, e.g., 'modifies', 'contradicts', 'reinforces'). If no dependencies, an empty list.\n\n"
                f"Legal Text Chunk: \"\"\"{chunk}\"\"\""
            )
            risk_analysis_output = await call_llm_api(risk_prompt, "risk_identification")

            # Prompt the LLM for jargon simplification
            jargon_prompt = (
                f"Rephrase the following legal text into plain English, explaining any complex jargon. "
                f"Provide a real-world example if it helps clarity. Return the rephrased text.\n\n"
                f"Legal Text Chunk: \"\"\"{chunk}\"\"\""
            )
            simplified_output = await call_llm_api(jargon_prompt, "jargon_simplification")

            # 3. Data Structuring for Frontend
            risk_level = risk_analysis_output.get("risk_level", "neutral")
            simplified_explanation = simplified_output.get("simplified_text", risk_analysis_output.get("simplified_explanation", "No specific explanation provided."))
            inter_dependencies = risk_analysis_output.get("inter_clause_dependencies", [])

            analysis_chunks.append(AnalysisResult(
                original_text_snippet=chunk,
                risk_level=risk_level,
                color_code=map_risk_to_color(risk_level),
                simplified_explanation=simplified_explanation,
                inter_clause_dependencies=inter_dependencies
            ))
            overall_summary_parts.append(f"Chunk {i+1} ({risk_level} risk): {simplified_explanation}")

        # Overall document summarization prompt
        overall_summary_prompt = (
            f"Provide a concise overall summary of the risks and key points identified in the document. "
            f"Focus on the most critical aspects. The document's analyzed chunks yielded these key points:\n\n"
            f"{' '.join(overall_summary_parts)}\n\n"
            f"Original document start (for context if needed):\n\n\"\"\"{raw_text[:2000]}\"\"\"" # Send a portion or reference if needed
        )
        overall_summary_output = await call_llm_api(overall_summary_prompt, "overall_summary")
        overall_summary_text = overall_summary_output.get("summary", "Overall summary could not be generated.")


        return FullAnalysisResponse(
            document_title="Analyzed Legal Document", # You might prompt LLM for this or use filename if uploaded
            total_chunks=len(analysis_chunks),
            analysis_chunks=analysis_chunks,
            overall_summary=overall_summary_text
        )

    except HTTPException as e:
        raise e # Re-raise FastAPI HTTPExceptions
    except Exception as e:
        logger.error(f"An unexpected error occurred during document analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# --- Stretch Goal: File Uploads ---
# You'll need to install 'python-multipart', 'PyPDF2', 'python-docx'
from PyPDF2 import PdfReader
import docx

@app.post("/upload-and-analyze", response_model=FullAnalysisResponse)
async def upload_and_analyze_document(file: UploadFile = File(...)):
    """
    Stretch Goal: Receives a document file (PDF or DOCX), extracts text, and performs analysis.
    """
    extracted_text = ""
    try:
        file_content = await file.read()
        if file.filename.endswith(".pdf"):
            logger.info(f"Processing PDF file: {file.filename}")
            reader = PdfReader(io.BytesIO(file_content))
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n"
        elif file.filename.endswith(".docx"):
            logger.info(f"Processing DOCX file: {file.filename}")
            document = docx.Document(io.BytesIO(file_content))
            for paragraph in document.paragraphs:
                extracted_text += paragraph.text + "\n"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or DOCX.")

        # Now call the existing analysis logic with the extracted text
        # We'll create a DocumentText object for this.
        # The 'analyze_document_text' endpoint doesn't directly use the Request object
        # for its internal logic (only for FastAPI's internal routing/dependency injection).
        # So we can just pass the DocumentText model.
        document_for_analysis = DocumentText(text=extracted_text)
        return await analyze_document_text(document_for_analysis)

    except HTTPException as e:
        raise e # Re-raise FastAPI HTTPExceptions
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")