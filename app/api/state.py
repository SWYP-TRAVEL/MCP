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
    

@router.get("/state", summary="get user status")
async def state(details: ItineraryDetail):
    return details

    
