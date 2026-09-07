# Fact Knowledge Layer

This is an open-ended assignment submission for Superjoin's Engineering Intern role.
The system is built to ingest PDFs, dynamically extract numerical and semantic facts, and discover relationships (corroborations, contradictions, contextual reconciliations) between documents using LLMs.

## Setup and Run Instructions

### Prerequisites
- Python 3.10+
- A Google Gemini API Key

### Installation

1. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your API Key in the environment (or in a `.env` file if you install `python-dotenv`):
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

### Running the System
1. **(Optional)** If you want to evaluate the UI offline without your own Gemini API key, the repository comes with a pre-populated SQLite database (`facts.db`) containing the extracted facts and relationships from the `delhivery` starter dataset out of the box.
2. Start the backend and frontend together:
   ```bash
   uvicorn backend.main:app --reload
   ```
3. Open your browser and navigate to `http://127.0.0.1:8000/`.

## Video Demo
[Insert Link to your 3-minute Video Demo Here]

## Approach
**Architecture**: 
- The backend is powered by **FastAPI**, serving both the API endpoints and the static frontend files.
- The UI is built using **Vanilla HTML/JS/CSS** emphasizing a clean, modern "glassmorphic" aesthetic.
- A **SQLite** database stores `Documents`, `Facts`, and their `Relationships`. 
- For PDF processing, **PyMuPDF** extracts text, which is chunked and passed to the **Gemini 2.5 Flash** model via the `google-genai` SDK.

**Logic Workflow**:
1. When a PDF is uploaded, it is parsed into text.
2. An LLM prompt instructs Gemini to act as a financial analyst and output an array of facts (with exact source evidence).
3. These new facts are cross-referenced with all existing facts in the system.
4. A second LLM prompt evaluates if new facts *corroborate*, *contradict*, or are *reconciled by context* against existing ones, automatically inserting these edges into our database.

**Trade-offs**:
- *Scalability vs Simplicity*: I chose SQLite and a monolithic FastAPI app for a simple, highly-understandable prototype. A production version would require a vector database for semantic search and async task queues (like Celery) for large document sets.
- *LLM Cost vs Precision*: To avoid hitting massive context windows or hallucination, I keep chunking simple for this prototype rather than building complex RAG pipelines. 

## Limitations and Next Steps
1. **Extraction and Reasoning Failure (Case 4)**: When parsing dense financial tables in `01-delhivery-prospectus-2022-excerpt.pdf` (e.g., page 23 multi-column restated balance sheets), PyMuPDF extracts text in reading order, merging column headers and associating metrics with the wrong year. The LLM extracted the restated loss as belonging to FY20 rather than FY19. We surfaced this under ambiguous extractions and flag tabular data with high uncertainty. **Next step**: Integrate a Vision-Language Model (VLM) for layout-aware parsing, or use specialized OCR models (like LayoutLM) before passing text to Gemini.
2. **Large Document Handling**: The system currently limits text processing chunks to avoid LLM context overflow. Next step: Implement smart chunking or a full RAG (Retrieval-Augmented Generation) pipeline.
3. **Fact Resolution**: If the LLM generates a hallucinated fact that doesn't trigger a hard JSON crash, the system doesn't automatically self-correct. Next step: Add a human-in-the-loop validation UI where users can edit/reject facts.

## Additional Notes
- Used a premium dark-mode UI design to make the discovery of contradictions feel like a professional analyst tool.
- Did not use TailwindCSS per explicit design instructions, achieving complex gradients and glass effects with pure CSS.
