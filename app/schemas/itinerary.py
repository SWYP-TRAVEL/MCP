"""
Itinerary schemas for API request/response models.
"""
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from datetime import date

class TravelWith(str, Enum):
    alone   = "alone"
    friends = "friends"
    family  = "family"
    lover   = "lover"

class ItineraryDetail(BaseModel):
    travel_with: TravelWith
    start_date: date
    end_date: date
    description: str
