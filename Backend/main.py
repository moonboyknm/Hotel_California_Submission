from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from pydantic import BaseModel
import re
import os
from typing import List, Dict, Any
import logging
import io
import google.generativeai as genai
import json

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
        if len(current_chunk) + len(sentence) + (1 if current_chunk else 0) <= max_chunk_size:
            current_chunk += (sentence + " ").strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = (sentence + " ").strip()
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

async def call_llm_api(prompt: str, task: str) -> Dict[str, Any]:
    """
    Makes an actual LLM API call to Google Gemini.
    """
    logger.info(f"Calling LLM for task: {task} with prompt sample: {prompt[:100]}...")

    try:
        genai.configure(api_key=LLM_API_KEY)
        model = genai.GenerativeModel(LLM_MODEL_NAME)

        if task in ["risk_identification"]:
            response = await model.generate_content_async(prompt)
            response_text = response.text

            # --- Extract JSON from markdown if present ---
            if response_text.startswith("```json"):
                response_text = response_text[len("```json"):].strip()
            if response_text.endswith("```"):
                response_text = response_text[:-len("```")].strip()

            try:
                parsed_response = json.loads(response_text)
                return parsed_response
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON for task {task}: {e}. Response: {response_text[:500]}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"LLM returned invalid JSON for {task}: {response_text[:100]}...")

        elif task in ["jargon_simplification", "overall_summary"]:
            response = await model.generate_content_async(prompt)
            response_text = response.text
            if task == "jargon_simplification":
                return {"simplified_text": response_text}
            elif task == "overall_summary":
                return {"summary": response_text}
        else:
            response = await model.generate_content_async(prompt)
            return {"analysis": response.text}

    except Exception as e:
        logger.error(f"LLM API call failed for task {task}: {e}", exc_info=True)
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
async def analyze_document_text(document: DocumentText):
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
            # --- USING PROMPT TEMPLATES HERE ---
            # Select the first prompt for risk identification and format it
            risk_prompt_template = PROMPT_TEMPLATES["risk_identification"][0]
            risk_prompt = risk_prompt_template.format(chunk=chunk)

            risk_analysis_output = await call_llm_api(risk_prompt, "risk_identification")

            # Select the first prompt for jargon simplification and format it
            jargon_prompt_template = PROMPT_TEMPLATES["jargon_simplification"][0]
            jargon_prompt = jargon_prompt_template.format(chunk=chunk)
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

        # --- USING PROMPT TEMPLATES HERE ---
        # Select the first prompt for overall summary and format it
        overall_summary_prompt_template = PROMPT_TEMPLATES["overall_summary"][0]
        overall_summary_prompt = overall_summary_prompt_template.format(
            summary_parts=' '.join(overall_summary_parts),
            raw_text_snippet=raw_text[:2000] # Provide a snippet of original text for context
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
        raise e
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

        document_for_analysis = DocumentText(text=extracted_text)
        return await analyze_document_text(document_for_analysis)

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")