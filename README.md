# 🎨 PixelPalettes: Legal Document Risk Analysis - LeDorian ⚖️

![GitHub Repo stars](https://img.shields.io/github/stars/moonboyknm/Hotel_California_Submission?style=social)
![GitHub forks](https://img.shields.io/github/forks/moonboyknm/Hotel_California_Submission?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/moonboyknm/Hotel_California_Submission)
![License](https://img.shields.io/github/license/moonboyknm/Hotel_California_Submission)

> 🔗 **GitHub Repository:** [moonboyknm/Hotel_California_Submission](https://github.com/moonboyknm/Hotel_California_Submission)

---

## 🏨 Team: Hotel California

---

## ✨ Project Overview

Our team, Hotel California, interprets "Pixel Palettes" as the exciting intersection of creativity and technology. This theme has inspired us to express complex ideas through visual and generative art, offering a unique lens through which to approach challenging problems. We see "Pixel Palettes" as an opportunity to transform traditionally dense and inaccessible information—specifically legal documents—into visually intuitive formats using a pixel-inspired design.

---

## ❓ The Problem We're Solving: Legal Document Risk Analysis

Legal policies, bills, and political drafts are often written using vague, biased, or overly complex language. This causes confusion or misinterpretation, allowing critical risks to go unnoticed. Our goal is to demystify this "legalese" and highlight potential hidden risks, making crucial legal information more accessible and transparent for the general public.

---

## 💡 Our Solution: Leveraging AI for Visual Storytelling

To address this, we use Large Language Models (LLMs) with a focus on identifying **inter-clause dependencies**, enabling our system to detect:

- ✅ Individual red-flag clauses  
- ⚠️ Compounding risks that arise from interacting clauses

Additionally, the LLMs handle:

- 📝 Summarizing lengthy legal sections  
- 🔍 Translating legal jargon into plain language  
- ⚠️ Detecting vague terms, biased language, and red flags  
- 🧱 Extracting document structure and external references

These insights are mapped onto a **color-coded, pixel-inspired visualization** — making legal risk understandable at a glance.

---

## 🖼️ Screenshots

> *Replace these placeholders with your actual screenshots once available*

### 🔹 Home Page
![Home Page](https://via.placeholder.com/800x400.png?text=Home+Page+UI)
*Main interface showing the document upload and navigation*

### 🔹 Document Upload and Analysis
![Analysis View](https://via.placeholder.com/800x400.png?text=Upload+and+Results+UI)
*Document analysis results with pixel-inspired risk visualization*

---

## 🛠️ Technical Architecture & Stack

A full-stack solution built with a Python backend and a React frontend.

### 🔧 Backend: FastAPI (Python)

- **Language:** Python 3.x  
- **Framework:** FastAPI  
- **LLM Integration:** `google-generativeai` with **Gemini 1.5 Flash**  
- **Document Parsing:** `PyPDF2`, `python-docx`  
- **Validation:** `Pydantic`  
- **Server:** `Uvicorn`

#### 🚀 Key Endpoints

- `POST /analyze-document-text`: Analyze raw text with prompt types (`detailed_analysis`, `risk_identification`, `jargon_simplification`, etc.)
- `POST /upload-and-analyze`: Accepts `PDF` or `DOCX`, extracts content, and analyzes

### 💻 Frontend: React + Vite

- **Language:** JavaScript (JSX), CSS  
- **Framework:** React  
- **Build Tool:** Vite  
- **HTTP Requests:** Axios  
- **Styling:** Custom pixel-inspired dark theme

---

## ⚙️ Git Management

A root `.gitignore` is configured to exclude:

- Python virtual environments (`venv/`, `BackVenv/`)  
- Bytecode (`__pycache__/`, `*.pyc`)  
- Node dependencies (`node_modules/`)  
- Build outputs (`dist/`, `.vite/`)  
- Environment files (`.env`, `*.env`)  
- IDE/OS-specific files (`.vscode/`, `.DS_Store`, `.idea/`)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+  
- Node.js (LTS recommended) & npm  
- Google Gemini API Key

### 1. Clone the Repository

```bash
git clone https://github.com/moonboyknm/Hotel_California_Submission.git
cd Hotel_California_Submission
```

### 2. Backend Setup

```bash
cd Backend
python3 -m venv BackVenv
source BackVenv/bin/activate  # On Windows: .\BackVenv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file inside `Backend/`:

```env
LLM_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY_HERE"
```

### 3. Frontend Setup

```bash
# In a new terminal
cd Frontend
npm install
npm install axios
```

### 4. Run the Application

**Terminal 1 (Backend):**

```bash
cd Backend
source BackVenv/bin/activate
uvicorn main:app --reload
```

Backend will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

**Terminal 2 (Frontend):**

```bash
cd Frontend
npm run dev
```

Frontend will be available at: [http://localhost:5173](http://localhost:5173)

---

## 🎯 Features

### Current Features
- **Document Upload:** Support for PDF and DOCX files
- **AI-Powered Analysis:** Gemini 1.5 Flash integration for comprehensive legal text analysis
- **Risk Detection:** Identification of red-flag clauses and inter-clause dependencies
- **Jargon Translation:** Conversion of legal language to plain English
- **RESTful API:** Well-structured endpoints for frontend-backend communication
- **Responsive UI:** Pixel-inspired dark theme interface

### Analysis Types
- **Detailed Analysis:** Comprehensive document breakdown
- **Risk Identification:** Highlights potential legal risks
- **Jargon Simplification:** Makes complex legal terms accessible
- **Structure Extraction:** Identifies document organization and references

---

## 🌟 Future Enhancements

- 🎨 **Pixel Grid Visualization:** Full visual abstraction of risks
- 🧠 **Interactive Clause Highlighting:** Click to see original text & AI explanations
- 🔐 **User Authentication & Sessions**
- 📂 **Document Storage, History & Versioning**
- 💬 **Expanded LLM Prompt Catalog**
- 📊 **Advanced Analytics Dashboard**
- 🔄 **Real-time Collaboration Features**

---

## 🤝 Contributing

We welcome contributions to make legal documents more accessible! Here's how you can help:

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

For major changes, please open an issue first to discuss what you'd like to change.

---

## 📋 API Documentation

### POST /analyze-document-text
Analyzes raw text input with specified analysis type.

**Request Body:**
```json
{
  "text": "Legal document text...",
  "prompt_type": "detailed_analysis"
}
```

**Response:**
```json
{
  "analysis": "AI-generated analysis...",
  "risk_level": "medium",
  "simplified_text": "Plain English version..."
}
```

### POST /upload-and-analyze
Uploads and analyzes PDF or DOCX files.

**Request:** Multipart form data with file upload
**Response:** Similar to text analysis endpoint

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Ensure Python 3.8+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify your Gemini API key is set in the `.env` file

**Frontend connection issues:**
- Make sure the backend is running on port 8000
- Check that Axios is properly installed: `npm install axios`
- Verify CORS settings in the FastAPI backend

**File upload problems:**
- Ensure uploaded files are valid PDF or DOCX format
- Check file size limits in the backend configuration

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## 👥 Team Members

**Hotel California Team:**
- Project Lead & AI Integration
- Frontend Development & UI/UX
- Backend Architecture & API Design
- Documentation & Testing

---

## 🙏 Acknowledgments

- Google Gemini AI for powerful language model capabilities
- FastAPI community for excellent documentation
- React and Vite teams for robust frontend tools
- Open source contributors who make projects like this possible

---

> 💡 **Made with focus and curiosity by Team Hotel California** 🏨  
> *Transforming complex legal documents into accessible, visual insights*

---

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/moonboyknm/Hotel_California_Submission/issues) page
2. Create a new issue with detailed description
3. Contact the team through the repository

**Happy analyzing!** ⚖️✨