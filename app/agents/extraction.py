import os
from dotenv import load_dotenv
import instructor
from groq import Groq

# Import the Quotation schema you built on Day 1
# Note: Adjust the import path if your file is named differently
from app.models.schemas import Quotation 

# Load environment variables (gets your GROQ_API_KEY)
load_dotenv()

# Initialize the Groq client and wrap it with Instructor
# This gives the client the "response_model" capability
client = instructor.from_groq(Groq(api_key=os.getenv("GROQ_API_KEY")))

def extract_quotation(raw_text: str) -> Quotation:
    """
    Takes raw, unstructured text from an email or document and 
    forces the Groq LLM to output a perfectly structured Quotation object.
    """
    
    print("🤖 Sending raw text to Groq for extraction...")
    
    # We use llama-3.3-70b-versatile or llama-3.1-8b-instant for fast, smart extraction
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_model=Quotation,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert procurement data extraction AI. "
                    "Your job is to extract quotation details from the provided text into the exact schema requested. "
                    "If a specific piece of information (like price, MOQ, or delivery days) is missing or unclear, "
                    "you MUST return null/None for that field. Do not guess or make up data."
                )
            },
            {
                "role": "user",
                "content": f"Extract the quotation details from this email:\n\n{raw_text}"
            }
        ],
    )
    
    return response

# ==========================================
# TEST THE EXTRACTION AGENT
# ==========================================
if __name__ == "__main__":
    # A messy, realistic email from a supplier
    sample_email = """
    Hi Yash,
    
    Thanks for reaching out. We can supply the Type 1 Portland Cement you requested.
    Our current price is $125.50 per ton. We require a minimum order of 50 tons for this rate.
    We can have it delivered to your Shirpur site in about 4 days. 
    Let me know if you want to proceed. This offer is good for the next 14 days.
    
    Best,
    Supplier ID: SUP-9942
    """
    
    try:
        # Run the extraction
        extracted_data = extract_quotation(sample_email)
        
        # Determine if it's complete
        if extracted_data.unit_price and extracted_data.moq and extracted_data.delivery_days:
            extracted_data.is_complete = True
            
        print("\n✅ Extraction Successful!")
        print("-" * 30)
        # print the result as a nice JSON string
        print(extracted_data.model_dump_json(indent=2))
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")