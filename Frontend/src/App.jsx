// Frontend/src/App.jsx
import React, { useState, useCallback } from 'react'; // Added useCallback
import axios from 'axios';
import './App.css'; // Import the CSS file

function App() {
  const [inputText, setInputText] = useState('');
  const [selectedPrompt, setSelectedPrompt] = useState('detailed_analysis'); // Default prompt type
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  // IMPORTANT: Ensure this URL matches your FastAPI server's address and port
  const API_BASE_URL = 'http://127.0.0.1:8000';

  const handleTextAnalysis = useCallback(async () => { // Wrapped in useCallback
    setError(null);
    setLoading(true);
    setAnalysisResult(null); // Clear previous results
    try {
      // Ensure this endpoint matches your FastAPI's @app.post("/analyze-document-text")
      const response = await axios.post(`${API_BASE_URL}/analyze-document-text`, {
        text: inputText,
        prompt_type: selectedPrompt,
      });
      setAnalysisResult(response.data);
    } catch (err) {
      console.error('Error during text analysis:', err);
      setError(err.response?.data?.detail || 'An unexpected error occurred during text analysis.');
    } finally {
      setLoading(false);
    }
  }, [inputText, selectedPrompt]); // Dependencies for useCallback

  const handleFileChange = useCallback((event) => { // Wrapped in useCallback
    setSelectedFile(event.target.files[0]);
  }, []);

  const handleFileUpload = useCallback(async () => { // Wrapped in useCallback
    if (!selectedFile) {
      setError('Please select a file to upload.');
      return;
    }

    setError(null);
    setLoading(true);
    setAnalysisResult(null); // Clear previous results

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Ensure this endpoint matches your FastAPI's @app.post("/upload-and-analyze")
      const response = await axios.post(`${API_BASE_URL}/upload-and-analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setAnalysisResult(response.data);
    } catch (err) {
      console.error('Error during file upload and analysis:', err);
      setError(err.response?.data?.detail || 'An unexpected error occurred during file upload and analysis.');
    } finally {
      setLoading(false);
    }
  }, [selectedFile]); // Dependencies for useCallback

  return (
    <div className="app-container">
      <h1>Legal Document AI Analyzer</h1>

      <div className="input-section">
        <textarea
          className="text-input"
          placeholder="Paste your legal document text here..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          rows="10"
        ></textarea>
        <div className="controls">
          <select
            value={selectedPrompt}
            onChange={(e) => setSelectedPrompt(e.target.value)}
            className="prompt-select"
          >
            <option value="risk_identification">Risk Identification</option>
            <option value="detailed_analysis">Detailed Analysis</option>
            <option value="jargon_simplification">Jargon Simplification</option>
            <option value="overall_summary">Overall Summary</option>
          </select>
          <button onClick={handleTextAnalysis} disabled={loading || !inputText.trim()} className="analyze-button">
            {loading ? 'Analyzing...' : 'Analyze Text'}
          </button>
        </div>
      </div>

      <div className="file-upload-section">
        <input type="file" onChange={handleFileChange} accept=".pdf,.docx" className="file-input" />
        <button onClick={handleFileUpload} disabled={loading || !selectedFile} className="upload-button">
          {loading ? 'Uploading...' : 'Upload & Analyze Document'}
        </button>
      </div>

      {error && <div className="error-message">Error: {error}</div>}

      {analysisResult && (
        <div className="results-section analysis-results-box"> {/* Use a class for styling the results container */}
          <h2>Analysis Results:</h2>

          {/* Always display Risk Level if available */}
          {analysisResult.risk_level && (
            <div className="result-item">
              <h3>Risk Level: <span className={`risk-level ${analysisResult.risk_level.toLowerCase()}`}>{analysisResult.risk_level}</span></h3>
            </div>
          )}

          {/* Always display Simplified Explanation if available */}
          {analysisResult.simplified_explanation && (
            <div className="result-item">
              <h3>Simplified Explanation:</h3>
              <p>{analysisResult.simplified_explanation}</p>
            </div>
          )}

          {/* Inter-Clause Dependencies - Common to both Risk and Detailed */}
          {analysisResult.inter_clause_dependencies && analysisResult.inter_clause_dependencies.length > 0 && (
            <div className="result-item">
              <h3>Inter-Clause Dependencies:</h3>
              <ul>
                {analysisResult.inter_clause_dependencies.map((dep, index) => (
                  <li key={index}>
                    <strong>Clause:</strong> {dep.clause_id} - <strong>Type:</strong> {dep.dependency_type} - <strong>Description:</strong> {dep.description}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Detailed Analysis Specific Fields */}
          {analysisResult.vague_terms && analysisResult.vague_terms.length > 0 && (
            <div className="result-item">
              <h3>Vague Terms:</h3>
              <ul>
                {analysisResult.vague_terms.map((term, index) => (
                  <li key={index}>
                    <strong>Term:</strong> "{term.term}" - <strong>Explanation:</strong> {term.explanation}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysisResult.biased_language && analysisResult.biased_language.length > 0 && (
            <div className="result-item">
              <h3>Biased Language:</h3>
              <ul>
                {analysisResult.biased_language.map((bias, index) => (
                  <li key={index}>
                    <strong>Phrase:</strong> "{bias.phrase}" - <strong>Explanation:</strong> {bias.explanation}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysisResult.red_flags && analysisResult.red_flags.length > 0 && (
            <div className="result-item">
              <h3>Red Flags:</h3>
              <ul>
                {analysisResult.red_flags.map((flag, index) => (
                  <li key={index}>
                    <strong>Type:</strong> {flag.type} - <strong>Description:</strong> {flag.description} - <strong>Original Text Snippet:</strong> "{flag.original_text_snippet}"
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysisResult.compounding_risks && analysisResult.compounding_risks.length > 0 && (
            <div className="result-item">
              <h3>Compounding Risks:</h3>
              <ul>
                {analysisResult.compounding_risks.map((risk, index) => (
                  <li key={index}>
                    <strong>Clauses Involved:</strong> {risk.clauses_involved.join(', ')} - <strong>Combined Risk Description:</strong> {risk.combined_risk_description}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysisResult.structural_elements && analysisResult.structural_elements.length > 0 && (
            <div className="result-item">
              <h3>Structural Elements:</h3>
              <ul>
                {analysisResult.structural_elements.map((elem, index) => (
                  <li key={index}>
                    <strong>Type:</strong> {elem.type} - <strong>Description:</strong> {elem.description}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysisResult.external_references && analysisResult.external_references.length > 0 && (
            <div className="result-item">
              <h3>External References:</h3>
              <ul>
                {analysisResult.external_references.map((ref, index) => (
                  <li key={index}>
                    <strong>Reference:</strong> {ref.reference} - <strong>Description:</strong> {ref.description}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysisResult.exception_clauses && analysisResult.exception_clauses.length > 0 && (
            <div className="result-item">
              <h3>Exception Clauses:</h3>
              <ul>
                {analysisResult.exception_clauses.map((clause, index) => (
                  <li key={index}>
                    <strong>Clause:</strong> {clause.clause} - <strong>Description:</strong> {clause.description}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysisResult.jurisdictional_risks && analysisResult.jurisdictional_risks.length > 0 && (
            <div className="result-item">
              <h3>Jurisdictional Risks:</h3>
              <ul>
                {analysisResult.jurisdictional_risks.map((risk, index) => (
                  <li key={index}>
                    <strong>Jurisdiction:</strong> {risk.jurisdiction} - <strong>Risk Description:</strong> {risk.risk_description} - <strong>Applicability:</strong> {risk.applicability}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Fallback for other prompt types that might return simpler JSON or unhandled structures */}
          {Object.keys(analysisResult).length > 0 && !analysisResult.risk_level && !analysisResult.simplified_explanation && (
            <div className="result-item">
              <h3>Raw Output (for unhandled structures or simple responses):</h3>
              <pre>{JSON.stringify(analysisResult, null, 2)}</pre>
            </div>
          )}

        </div>
      )}
    </div>
  );
}

export default App;