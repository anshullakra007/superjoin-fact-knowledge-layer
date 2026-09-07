from fastapi import FastAPI, UploadFile, File, Depends, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import os
import shutil
from dotenv import load_dotenv

load_dotenv()

from . import models, database, extraction

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Fact Knowledge Layer API")

# Serve the frontend files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("frontend/index.html", "r") as f:
        return f.read()

@app.post("/api/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Create DB entry
    db_doc = models.Document(filename=file.filename)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # Process in background so API responds quickly
    background_tasks.add_task(process_pdf, file_path, db_doc.id, db)
    
    return {"message": "File uploaded and processing started.", "doc_id": db_doc.id}

def process_pdf(file_path: str, doc_id: int, db: Session):
    try:
        pages = extraction.extract_text_from_pdf(file_path)
        
        all_new_facts = []
        # For prototype, let's process page by page or a chunk of pages
        # To avoid massive context, we can just process first 3 pages if it's long, or loop.
        for page_num, text in pages.items():
            if not text.strip():
                continue
            
            # Very basic chunking to not overwhelm if page is huge
            facts_response = extraction.extract_facts_with_llm(text[:20000]) # Cap text length
            
            if not facts_response.get("success"):
                db_fail = models.Failure(
                    doc_id=doc_id,
                    error_type=facts_response.get("error_type"),
                    raw_output=facts_response.get("raw_output"),
                    context=facts_response.get("context")
                )
                db.add(db_fail)
                continue
                
            facts_data = facts_response.get("data", [])
            for fact_data in facts_data:
                statement = fact_data.get("statement", "")
                if not statement:
                    continue
                db_fact = models.Fact(
                    doc_id=doc_id,
                    statement=statement,
                    evidence=fact_data.get("evidence", ""),
                    page_number=page_num
                )
                db.add(db_fact)
                all_new_facts.append(fact_data) # Keep dict for LLM relationship prompt
                
        db.commit()
        
        # Now re-fetch to get IDs for the new facts to map them
        new_db_facts = db.query(models.Fact).filter(models.Fact.doc_id == doc_id).all()
        
        existing_facts = db.query(models.Fact).filter(models.Fact.doc_id != doc_id).all()
        
        # If we have existing facts, we analyze relationships
        if existing_facts and new_db_facts:
            # We need to pass the new dicts but with their DB IDs
            new_facts_for_llm = []
            for fact in new_db_facts:
                new_facts_for_llm.append({
                    "id": fact.id,
                    "statement": fact.statement
                })
                
            relationships_response = extraction.analyze_relationships_with_llm(new_facts_for_llm, existing_facts)
            
            if not relationships_response.get("success"):
                db_fail = models.Failure(
                    doc_id=doc_id,
                    error_type=relationships_response.get("error_type"),
                    raw_output=relationships_response.get("raw_output"),
                    context=relationships_response.get("context")
                )
                db.add(db_fail)
            else:
                relationships = relationships_response.get("data", [])
                for rel in relationships:
                    existing_id = rel.get("existing_fact_id")
                    new_id = rel.get("new_fact_id")
                    
                    # Check if new_id is our custom format "NEW_idx" or if LLM returned actual ID
                    if isinstance(new_id, str) and new_id.startswith("NEW_"):
                        try:
                            idx = int(new_id.split("_")[1])
                            actual_new_id = new_db_facts[idx].id
                        except:
                            actual_new_id = None
                    else:
                        actual_new_id = new_id
                        
                    if existing_id and actual_new_id:
                        db_rel = models.Relationship(
                            fact1_id=existing_id,
                            fact2_id=actual_new_id,
                            relationship_type=rel.get("relationship_type", "unknown"),
                            explanation=rel.get("explanation", "")
                        )
                        db.add(db_rel)
            db.commit()
            
    except Exception as e:
        print(f"Error processing document {doc_id}: {e}")

@app.get("/api/facts")
def get_facts(db: Session = Depends(database.get_db)):
    facts = db.query(models.Fact).all()
    result = []
    for f in facts:
        doc = db.query(models.Document).filter(models.Document.id == f.doc_id).first()
        result.append({
            "id": f.id,
            "statement": f.statement,
            "evidence": f.evidence,
            "page_number": f.page_number,
            "document": doc.filename if doc else "Unknown"
        })
    return result

@app.get("/api/relationships")
def get_relationships(db: Session = Depends(database.get_db)):
    rels = db.query(models.Relationship).all()
    result = []
    for r in rels:
        f1 = db.query(models.Fact).filter(models.Fact.id == r.fact1_id).first()
        f2 = db.query(models.Fact).filter(models.Fact.id == r.fact2_id).first()
        
        doc1 = db.query(models.Document).filter(models.Document.id == f1.doc_id).first() if f1 else None
        doc2 = db.query(models.Document).filter(models.Document.id == f2.doc_id).first() if f2 else None
        
        result.append({
            "id": r.id,
            "type": r.relationship_type,
            "explanation": r.explanation,
            "fact1": {
                "statement": f1.statement if f1 else "",
                "document": doc1.filename if doc1 else ""
            },
            "fact2": {
                "statement": f2.statement if f2 else "",
                "document": doc2.filename if doc2 else ""
            }
        })
    return result

@app.get("/api/documents")
def get_documents(db: Session = Depends(database.get_db)):
    docs = db.query(models.Document).all()
    return [{"id": d.id, "filename": d.filename} for d in docs]

@app.get("/api/failures")
def get_failures(db: Session = Depends(database.get_db)):
    failures = db.query(models.Failure).all()
    result = []
    for f in failures:
        doc = db.query(models.Document).filter(models.Document.id == f.doc_id).first()
        result.append({
            "id": f.id,
            "error_type": f.error_type,
            "raw_output": f.raw_output,
            "context": f.context,
            "document": doc.filename if doc else "Unknown"
        })
    return result

@app.post("/api/simulate-failure")
def simulate_failure(db: Session = Depends(database.get_db)):
    db_fail = models.Failure(
        doc_id=None,
        error_type="JSONDecodeError",
        raw_output="Unterminated string starting at: line 1 column 15 (char 14)",
        context="Failed to parse LLM relationship output as JSON."
    )
    db.add(db_fail)
    db.commit()
    return {"message": "Failure simulated"}
