import sys
import os
# This tells Python to look two folders up (the root directory) for the 'app' module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.parsing.document_parser import extract_text_from_pdf
from app.agents.extraction import extract_quotation

def run_pdf_extraction_test():
    # 1. Point this to a real or dummy PDF on your machine
    pdf_path = "data/raw/PostgreSQL Storage Layer.pdf" 
    
    # 2. Extract the raw text from the PDF
    raw_pdf_text = extract_text_from_pdf(pdf_path)
    
    if not raw_pdf_text:
        print("Failed to get text from PDF. Check file path.")
        return
        
    print("\n--- Extracted Raw Text ---")
    print(raw_pdf_text[:500] + "...\n[TRUNCATED]") 
    
    # 3. Pass the raw text to your Groq Agent!
    print("\n--- Handing off to Groq Extraction Agent ---")
    result = extract_quotation(raw_pdf_text, supplier_id="PDF-SUPPLIER-01")
    
    if result:
        print("\n✅ Final Structured JSON:")
        print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    run_pdf_extraction_test()