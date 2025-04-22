from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from datetime import date
router = APIRouter(prefix="/api")

class TravelWith(str, Enum):
    alone   = "alone",
    friends = "firends",
    family  = "family",
    lover   =  "lovel"

class ItineraryDetail(BaseModel):
    travel_with: TravelWith
    start_date: date
    end_date: date
    description: str
    

@router.get("/create", summary="itinerary creation request")
async def create(itinerary_details: ItineraryDetail):
    return itinerary_details

    
