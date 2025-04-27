from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from datetime import date
from clients import client

from agents import gen_trace_id, trace
from agents.mcp import MCPServerSse

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
    async with MCPServerSse (
        name="mcp_server",
        params= {
            "url": "http://localhost:8070/sse"
        }, 
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Travel", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            client.run(server, itinerary_details)
    return itinerary_details

