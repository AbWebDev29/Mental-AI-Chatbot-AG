from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PatientSession(BaseModel):
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # The 3-9 Scale from your theory
    intensity_score: int = Field(..., ge=3, le=9, description="The 3-9 mental health scale intensity")
    
    # Clinical Context Tags
    context: List[str] = [] # e.g., ["Workplace", "Insomnia", "Hinglish"]
    
    # The actual conversation data
    user_message: str
    ai_response: str
    
    # Differential Logic markers
    primary_struggle: Optional[str] = None # e.g., "Overthinking" or "Panic"