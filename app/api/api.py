from fastapi import APIRouter
from schemas.itinerary import ItineraryDetail
from create.client import create_itinerary, create_suggestion
from triplet.client import triplet_manager
from agents.mcp import MCPServerSse
from agents import gen_trace_id, trace

router = APIRouter(prefix="/api")

@router.post("/create", summary="itinerary creation request")
async def create(itinerary: ItineraryDetail):
    print(itinerary)
    async with MCPServerSse(
        name="create_itinerary_mcp_server",
        params={
            "url": "http://localhost:8070/sse",
        }
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Travel", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            res = await create_itinerary(server, itinerary)
    return res

@router.post("/triplet", summary="listup for 3 course")      
async def triplet(itinerary: ItineraryDetail):
    async with MCPServerSse(
        name="triplet_mcp_server",
        params={
            "url": "http://localhost:8071/sse",
        }
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="Travel", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            res = await triplet_manager(server, itinerary)
    return res

@router.post("/suggest_discription", summary="suggest discription")
async def suggest():
    trace_id = gen_trace_id()
    with trace(workflow_name="Travel", trace_id=trace_id):
        print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
    res = await create_suggestion()
    return res