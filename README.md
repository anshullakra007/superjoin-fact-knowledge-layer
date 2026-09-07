# Fact Knowledge Layer

Hello! This is my submission for Superjoin's Engineering Intern role.

The goal of this project was to build a system that moves beyond simple text ingestion and actively understands the content. This application extracts numerical and semantic facts from financial PDFs and acts as an automated analyst—cross-referencing those facts against existing data to discover corroborations, flag contradictions, and reconcile context-based discrepancies using LLMs.

---

## Setup and Run Instructions

I have aimed to keep the setup as frictionless as possible. You will need:
- Python 3.10+
- A Google Gemini API Key

### Getting Started

1. **Initialize a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install the requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure your API Key**: Set your Gemini API key in your environment (or use a `.env` file).
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

### Running the System
1. **(Optional) Offline Evaluation**: If you would like to explore the UI immediately without using your own Gemini API key, the repository includes a pre-populated SQLite database (`facts.db`). It contains the fully extracted knowledge graph from the `delhivery` starter dataset.
2. **Start the backend server**:
   ```bash
   uvicorn backend.main:app --reload
   ```
3. **View the application**: Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## Video Demo
[Insert Link to your 3-minute Video Demo Here]

---

## Approach

When designing this system, I focused on a lean, transparent architecture rather than over-engineering it with heavy frameworks. 

**The Tech Stack**: 
- **Backend**: Built with **FastAPI** for its speed, modern design, and readability. It serves both the API endpoints and the static frontend.
- **Frontend**: Built entirely with **Vanilla HTML/JS/CSS**. I wanted to demonstrate that a premium, glassmorphic UI can be achieved without relying on component libraries like React or CSS frameworks like Tailwind.
- **Database**: A lightweight **SQLite** database stores `Documents`, `Facts`, and `Relationships`. 
- **AI & Parsing**: **PyMuPDF** handles the raw text extraction, which is then passed to the **Gemini 2.5 Flash** model via the `google-genai` SDK.

**How it works under the hood**:
1. Upon uploading a PDF, the backend extracts the raw text.
2. Gemini acts as an extraction engine, pulling out hard facts and explicitly citing the exact verbatim quote and page number as evidence.
3. The system then compares these new facts against the entire existing knowledge base.
4. A second Gemini prompt acts as a "Reasoning Engine." It evaluates if the new facts *corroborate*, *contradict*, or are *reconciled by context* (like differing fiscal years) against existing knowledge, automatically mapping these relationships in the database.

**Design Trade-offs**:
- *Understandability over Extreme Scale*: I chose SQLite and a monolithic FastAPI application so the codebase remains highly readable and easy to review. For a production system handling thousands of documents, I would migrate to a vector database for semantic search and an asynchronous worker queue (like Celery).
- *Cost vs. Precision*: I kept the document chunking straightforward for this prototype to avoid exceeding context windows or incurring heavy API costs, rather than building a complex multi-stage RAG pipeline. 

---

## Limitations and Next Steps

No system is perfect, and I want to be entirely transparent about where this specific approach encounters challenges (Case 4):

1. **Extraction and Reasoning Failure**: When parsing dense financial tables in `01-delhivery-prospectus-2022-excerpt.pdf` (specifically the multi-column restated balance sheets on page 23), PyMuPDF reads the text linearly. This merges column headers and associates metrics with the wrong year, causing the LLM to hallucinate that a restated loss belonged to FY20 rather than FY19. I have surfaced this in the UI under a "System Diagnostics" panel to catch these ambiguities gracefully. 
   * **Next step**: Raw text extraction is the core bottleneck here. Integrating a Vision-Language Model (VLM) for layout-aware parsing, or utilizing a specialized OCR model (like LayoutLM) before passing data to Gemini, would resolve this.
2. **Large Document Handling**: The system currently limits text processing chunks to avoid context overflow. 
   * **Next step**: Implement a more advanced chunking strategy or a full Retrieval-Augmented Generation (RAG) pipeline.
3. **Fact Resolution**: If the LLM generates an inaccurate fact that does not trigger a hard JSON crash, the system does not automatically self-correct. 
   * **Next step**: Build a "human-in-the-loop" UI where analysts can manually verify, edit, or reject the extracted facts.

---

## Additional Notes
- I purposefully designed a premium dark-mode UI. Discovering contradictions in financial reports should feel like using a modern analyst tool, not a raw spreadsheet.
- I strictly adhered to the design constraints and avoided TailwindCSS, achieving the complex gradients and glass effects entirely with custom CSS. 

Thank you for taking the time to review my submission!
