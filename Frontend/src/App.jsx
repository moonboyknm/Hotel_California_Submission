// Frontend/src/App.jsx
import React, { useState } from 'react';
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

  const handleTextAnalysis = async () => {
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
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleFileUpload = async () => {
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
  };

  // Helper to render complex JSON objects
  const renderResult = (data) => {
    if (!data) return null;

    return (
      <div className="analysis-output">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="output-section">
            <h3>{key.replace(/_/g, ' ').toUpperCase()}</h3>
            {Array.isArray(value) ? (
              value.length > 0 ? (
                <ul>
                  {value.map((item, index) => (
                    <li key={index}>
                      {typeof item === 'object' ? JSON.stringify(item, null, 2) : item}
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No {key.replace(/_/g, ' ')} identified.</p>
              )
            ) : typeof value === 'object' ? (
              renderResult(value) // Recursively render nested objects
            ) : (
              <p>{value}</p>
            )}
          </div>
        ))}
      </div>
    );
  };

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
        <div className="results-section">
          <h2>Analysis Results:</h2>
          {renderResult(analysisResult)}
        </div>
      )}
    </div>
  );
}

export default App;