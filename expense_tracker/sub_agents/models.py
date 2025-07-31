from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class ExpenseCategory(str, Enum):
    MEALS_ENTERTAINMENT = "Meals & Entertainment"
    TRAVEL_TRANSPORT = "Travel & Transport"
    ACCOMODATION = "Accommodation"
    GROCERIES = "Groceries"
    OFFICE_SUPPLIES = "Office Supplies"
    UTILITIES_TELECOM = "Utilities & Telecom"
    HEALTH_WELLNESS = "Health & Wellness"
    OTHER = "Other"

class Item(BaseModel):
    """Represents a single line item from a categorized receipt."""
    description: str
    unit_price: float
    quantity: int
    line_total: float
    category: ExpenseCategory
    confidence: float = Field(..., ge=0.00, le=1.0) # Confidence must be between 00 and 1.0

class CategorizedItems(BaseModel):
    """Represents the full list of categorized items from a receipt."""
    items: List[Item]
