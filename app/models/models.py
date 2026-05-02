import operator
from typing import List, Optional, Annotated, TypedDict
from pydantic import BaseModel, Field, EmailStr

# ==========================================
# TASK 2: CORE PYDANTIC MODELS
# ==========================================

class Supplier(BaseModel):
    """Schema representing a construction material supplier."""
    id: str = Field(description="Unique identifier for the supplier (e.g., UUID or DB ID)")
    name: str = Field(description="Official name of the supplier company")
    material_categories: List[str] = Field(description="List of materials they supply (e.g., ['cement', 'steel'])")
    email: EmailStr = Field(description="Contact email address for quotation requests")
    
    # Optional fields for scoring and tracking later
    trust_score: Optional[float] = Field(default=None, description="Calculated composite trust score")
    is_cold_start: bool = Field(default=True, description="Flag indicating if there is no prior history with this supplier")

class Quotation(BaseModel):
    """Schema representing a structured quotation extracted from an email or PDF."""
    supplier_id: str = Field(description="The ID of the supplier who provided this quote")
    unit_price: Optional[float] = Field(default=None, description="The price per unit offered")
    currency: Optional[str] = Field(default="USD", description="Currency of the quote (e.g., USD, EUR, INR)")
    moq: Optional[int] = Field(default=None, description="Minimum Order Quantity required")
    delivery_days: Optional[int] = Field(default=None, description="Estimated number of days for delivery")
    validity_period: Optional[int] = Field(default=None, description="Number of days this quote remains valid")
    
    # Boolean flag to easily check if the Extraction Agent got everything
    is_complete: bool = Field(
        default=False, 
        description="True if unit_price, moq, and delivery_days are all successfully extracted"
    )

# ==========================================
# TASK 3: LANGGRAPH STATE MODEL
# ==========================================

class ProcurementState(TypedDict):
    """
    The shared state dictionary that flows through the LangGraph agents.
    
    Using Annotated[List[...], operator.add] acts as a reducer. 
    When an agent returns a dictionary like {"quotes": [new_quote]}, 
    LangGraph will append it to the existing list rather than overwriting it.
    """
    
    # The original request from the user (e.g., "We need 500 tons of cement")
    request: str
    
    # The required material identified by the Supervisor
    target_material: str
    
    # List of suppliers discovered. Appends new suppliers.
    suppliers: Annotated[List[Supplier], operator.add]
    
    # List of successfully extracted quotations. Appends new quotes.
    quotes: Annotated[List[Quotation], operator.add]
    
    # Current status of the workflow (e.g., "pending_quotes", "ready_for_scoring")
    status: str