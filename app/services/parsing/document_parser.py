import os
import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    """
    Reads a PDF file locally and extracts all text, preserving 
    table structures as much as possible for the LLM.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find file at: {file_path}")
    
    print(f"📄 Parsing PDF: {os.path.basename(file_path)}...")
    
    extracted_text = ""
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                # Extract text, preserving layout for tables
                text = page.extract_text(layout=True)
                if text:
                    extracted_text += f"\n--- PAGE {i+1} ---\n{text}"
                    
        return extracted_text.strip()
        
    except Exception as e:
        print(f"❌ Error parsing PDF: {e}")
        return ""