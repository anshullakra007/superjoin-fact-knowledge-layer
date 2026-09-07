# Fact Knowledge Layer

Hello! This is my submission for Superjoin's Engineering Intern role. 

The goal here was to build a system that doesn't just blindly ingest PDFs, but actually *understands* them. This application extracts numerical and semantic facts, and then acts like an automated analyst—cross-referencing those facts against everything else in the system to discover corroborations, flag contradictions, and reconcile tricky context-based discrepancies using LLMs.

---

## Setup and Run Instructions

I've kept the setup as frictionless as possible. You'll just need:
- Python 3.10+
- A Google Gemini API Key

### Getting Started

1. **Spin up a virtual environment** so we don't clutter your global packages:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install the requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Add your API Key**: Set your Gemini API key in your environment. (You can also drop it in a `.env` file).
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

### Running the System
1. **(Optional) Offline Mode**: If you want to poke around the UI right away without hitting your own Gemini API key limits, I've got you covered. The repository comes with a pre-populated SQLite database (`facts.db`) containing the fully extracted knowledge graph from the `delhivery` starter dataset.
2. **Boot up the server**:
   ```bash
   uvicorn backend.main:app --reload
   ```
3. **Check it out**: Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## Video Demo
[Insert Link to your 3-minute Video Demo Here]

---

## Approach

When designing this, I focused on keeping the architecture lean and transparent rather than over-engineering it with heavy frameworks. 

**The Tech Stack**: 
- **Backend**: I went with **FastAPI** because it's fast, modern, and incredibly easy to read. It serves both the API endpoints and the static frontend.
- **Frontend**: Built entirely with **Vanilla HTML/JS/CSS**. I wanted to show that you can build a premium, glassmorphic UI without relying on Tailwind or React.
- **Database**: A lightweight **SQLite** database stores `Documents`, `Facts`, and `Relationships`. 
- **AI/Parsing**: **PyMuPDF** handles the raw text extraction, which is then passed to the **Gemini 2.5 Flash** model via the `google-genai` SDK.

**How it works under the hood**:
1. You upload a PDF, and the backend rips the text out.
2. Gemini acts as an extraction engine, pulling out hard facts and explicitly citing the exact verbatim quote and page number as evidence.
3. The system then compares these new facts against *everything* currently in the database.
4. A second Gemini prompt acts as the "Reasoning Engine." It evaluates if the new facts *corroborate*, *contradict*, or are *reconciled by context* (like differing fiscal years) against existing knowledge, automatically wiring up relationships in the database.

**Trade-offs I made**:
- *Understandability over Extreme Scale*: I chose SQLite and a monolithic FastAPI app so the codebase is easy to review. If this were a production system handling thousands of docs, I would swap this out for a vector DB (for semantic search) and an async worker queue (like Celery).
- *Cost vs Precision*: I kept the document chunking relatively simple for this prototype to avoid blowing up context windows or incurring massive API costs, rather than building a heavy multi-stage RAG pipeline. 

---

## Limitations and Next Steps

No system is perfect, and I wanted to be totally transparent about where this approach breaks down (Case 4):

1. **Extraction and Reasoning Failure**: When parsing incredibly dense financial tables in `01-delhivery-prospectus-2022-excerpt.pdf` (specifically the multi-column restated balance sheets on page 23), PyMuPDF reads the text linearly. This merges column headers and associates metrics with the wrong year, causing the LLM to hallucinate that a restated loss belonged to FY20 rather than FY19. I surfaced this in the UI under a "System Diagnostics" panel to catch these ambiguities gracefully. 
   * **Next step**: Raw text extraction is the bottleneck here. I would integrate a Vision-Language Model (VLM) for layout-aware parsing or run the docs through a specialized OCR model (like LayoutLM) before passing anything to Gemini.
2. **Large Document Handling**: The system currently limits text processing chunks to avoid context overflow. 
   * **Next step**: Implement a smarter chunking strategy or a full Retrieval-Augmented Generation (RAG) pipeline.
3. **Fact Resolution**: If the LLM generates a hallucinated fact that doesn't trigger a hard JSON crash, the system doesn't automatically self-correct. 
   * **Next step**: Build a "human-in-the-loop" UI where analysts can manually accept, edit, or reject the extracted facts.

---

## Additional Notes
- I purposefully designed a premium dark-mode UI. Discovering contradictions in financial reports should feel like using a state-of-the-art analyst tool, not a spreadsheet.
- I stuck strictly to the design constraints and avoided TailwindCSS, achieving the complex gradients and glass effects entirely with custom CSS. 

Thanks for taking the time to review my submission!
