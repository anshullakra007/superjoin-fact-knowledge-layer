import os
import fitz  # PyMuPDF
import json
from google import genai
from google.genai import types

def extract_text_from_pdf(pdf_path: str) -> dict:
    """Extracts text from a PDF and returns a mapping of page numbers to text."""
    doc = fitz.open(pdf_path)
    pages = {}
    for page_num in range(len(doc)):
        page = doc[page_num]
        pages[page_num + 1] = page.get_text()
    return pages

def extract_facts_with_llm(text: str) -> list:
    """Uses Gemini to extract facts from text."""
    # Ensure API key is set in environment: GEMINI_API_KEY
    if not os.environ.get("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY not set. Cannot extract facts.")
        return []
    
    client = genai.Client()
    
    prompt = """
    You are an expert financial and corporate analyst.
    Read the following text from a company document or economic report.
    Extract key numerical and semantic facts. 
    
    For each fact, provide:
    1. "statement": A clear, concise statement of the fact (e.g., "Delhivery's revenue in FY24 was Rs. X.")
    2. "evidence": The exact quote from the text that supports this fact.
    3. "confidence": High, Medium, or Low based on how clear the text is.
    
    Output the response as a JSON array of objects. Do not wrap it in markdown block like ```json ... ```, just the array itself, for example:
    [
      {
        "statement": "Fact 1",
        "evidence": "Quote 1"
      }
    ]
    
    TEXT:
    """ + text
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        # Parse the JSON response
        facts = json.loads(response.text)
        if isinstance(facts, list):
            return facts
        return []
    except Exception as e:
        print(f"Error during LLM extraction: {e}")
        return []

def analyze_relationships_with_llm(new_facts: list, existing_facts: list) -> list:
    """Compares new facts against existing facts to find relationships."""
    if not existing_facts or not new_facts:
        return []
        
    if not os.environ.get("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY not set. Cannot analyze relationships.")
        return []

    client = genai.Client()
    
    prompt = f"""
    You are an expert fact-checker and analyst.
    You will be provided with a list of "Existing Facts" from our knowledge base, and a list of "New Facts" just extracted from a new document.
    
    Compare the New Facts against the Existing Facts. Identify if any New Fact:
    1. "corroborates": Directly supports or confirms an Existing Fact.
    2. "contradicts": Directly contradicts an Existing Fact (e.g., different revenue numbers for the same period).
    3. "reconciled": Initially appears to contradict, but can be explained by context (e.g., different time periods, different units, standalone vs consolidated).
    
    Existing Facts (ID: Statement):
    """
    
    for f in existing_facts:
        prompt += f"- ID {f.id}: {f.statement}\n"
        
    prompt += "\nNew Facts:\n"
    for idx, f in enumerate(new_facts):
        prompt += f"- ID NEW_{idx}: {f.get('statement')}\n"
        
    prompt += """
    Output ONLY a JSON array of relationship objects. Do not wrap in markdown. Format:
    [
      {
        "existing_fact_id": 123,
        "new_fact_id": "NEW_0", 
        "relationship_type": "corroborates", // or "contradicts" or "reconciled"
        "explanation": "Both documents state the revenue is 5000."
      }
    ]
    If there are no notable relationships, output an empty array [].
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        relationships = json.loads(response.text)
        if isinstance(relationships, list):
            return relationships
        return []
    except Exception as e:
        print(f"Error during LLM relationship analysis: {e}")
        return []
