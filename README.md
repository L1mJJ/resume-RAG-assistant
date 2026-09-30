# Resume RAG Assistant

![Python](https://img.shields.io/badge/Python-3776AB?logo=python\&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?logo=google\&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Database-FF6B6B)
![Sentence Transformers](https://img.shields.io/badge/Sentence%20Transformers-Embeddings-FF6F00)

A lightweight RAG-based resume assistant that allows users to upload a resume and ask questions about its contents. Resume information is embedded and stored in ChromaDB, allowing relevant sections to be retrieved before generating an answer with Google Gemini.

Built from scratch without LangChain to explore the core components of a Retrieval-Augmented Generation pipeline.

## Features

* PDF text extraction with `pypdf`
* Gemini OCR fallback for image-based resumes
* Semantic search using Sentence Transformers
* Persistent vector storage with ChromaDB
* Candidate identification using email addresses
* Grounded responses using retrieved resume context
* Automatic replacement of outdated resumes for the same candidate

## Tech Stack

| Technology            | Purpose                         |
| --------------------- | ------------------------------- |
| Python                | Application logic               |
| pypdf                 | PDF text extraction             |
| Sentence Transformers | Text embeddings                 |
| ChromaDB              | Vector storage and retrieval    |
| Google Gemini         | OCR and response generation     |
| python-dotenv         | Environment variable management |

## Installation

```bash
git clone <repository-url>
cd resume-rag

pip install -r requirements.txt
```

## Requirements

* Python 3.10+
* Google Gemini API key
* Internet connection for Gemini API access and initial model download
* Resume in PDF format

Dependencies are listed in `requirements.txt`:

```text
pypdf
sentence-transformers
chromadb
google-genai
python-dotenv
```

## API Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

The `.env` file is excluded from version control.

## Usage

Start the application:

```bash
python resume_rag.py
```

Enter the path to a resume when prompted:

```text
Enter the path to the resume PDF: C:\path\to\resume.pdf
```

Once the resume has been processed, enter a question:

```text
Ask a question about the resume: What are their technical skills?
```

The application retrieves the most relevant resume chunks and passes them to Gemini to generate the final response.

## Privacy & Data Handling

Resumes may contain sensitive personal information. This project is intended for local experimentation and should only be used with resumes you have permission to process.

* Resume PDFs are processed locally by the application.
* Extracted resume text is stored locally in ChromaDB.
* Resume embeddings are stored locally in the `chroma_db/` directory.
* If `pypdf` cannot extract text, the PDF is uploaded to Google Gemini for OCR processing.
* Retrieved resume content is sent to Google Gemini when generating an answer.
* API keys are stored locally in `.env` and should never be committed to the repository.
* Resume files and the local ChromaDB database are excluded from Git through `.gitignore`.

Do not upload real resumes containing personal information to a public repository.

## Architecture

```text
                 ┌──────────────┐
                 │  Resume PDF  │
                 └──────┬───────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Text Extraction   │
              │ pypdf / Gemini    │
              └─────────┬─────────┘
                        │
                        ▼
                 ┌────────────┐
                 │  Chunking  │
                 └─────┬──────┘
                       │
                       ▼
              ┌───────────────────┐
              │    Embeddings     │
              │ MiniLM-L6-v2      │
              └─────────┬─────────┘
                        │
                        ▼
                 ┌────────────┐
                 │ ChromaDB   │
                 └─────┬──────┘
                       │
              User Question
                       │
                       ▼
              ┌────────────────┐
              │ Semantic Search│
              └───────┬────────┘
                      │
                      ▼
              ┌────────────────┐
              │ Google Gemini  │
              └───────┬────────┘
                      │
                      ▼
                    Answer
```

## Project Structure

```text
resume-rag/
├── resume_rag.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
└── chroma_db/
```

`.env` and `chroma_db/` are excluded from Git.

## Functions

| Function                     | Description                                       |
| ---------------------------- | ------------------------------------------------- |
| `extract_text_with_gemini()` | Extracts text from image-based PDFs using Gemini  |
| `extract_email()`            | Extracts the candidate's email for identification |
| `clean_text()`               | Cleans extracted resume text                      |
| `chunk_text()`               | Splits resume text into retrieval-friendly chunks |

The main RAG pipeline handles embedding generation, vector storage, semantic retrieval, and response generation.

## Future Enhancements

* Multiple-resume querying
* Section-aware and overlapping chunking
* Resume metadata and filtering
* Candidate comparison
* Hybrid search
* Web interface
* Retrieval and answer evaluation

## Credits

* [Google Gemini](https://ai.google.dev/)
* [ChromaDB](https://www.trychroma.com/)
* [Sentence Transformers](https://www.sbert.net/)
* [pypdf](https://pypdf.readthedocs.io/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)