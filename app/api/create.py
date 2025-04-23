from fastapi import APIRouter, HTTPException
from schemas import ItineraryDetail
from clients.client import run
from agents.mcp import MCPServer, MCPServerSse

router = APIRouter(prefix="/api")

@router.get("/create", summary="itinerary creation request")
async def create(itinerary_details: ItineraryDetail):
    async with MCPServerSse(
        name="SSE Travel Server",
        params = {
            "url": "http://localhost:8000/sse",
        }
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="SSE Example", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)
    return itinerary_details
