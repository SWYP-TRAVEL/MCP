import asyncio
from typing import List
from pydantic import BaseModel
from agents import Agent, Runner, gen_trace_id, trace, ModelSettings,OpenAIChatCompletionsModel, AsyncOpenAI
from agents.mcp import MCPServer, MCPServerSse
from schemas.itinerary import ItineraryDetail


class Schadule(BaseModel):
    day_date: int
    breakfast_online_summary: str
    launch: str
    launch_online_summary: str
    dinner: str
    dinner_online_summary: str
    attraction1: str
    attraction1_online_summary: str
    attraction2: str
    attraction2_online_summary: str

def itinerary_detail_to_prompt(itinerary_detail: ItineraryDetail) -> str:
    return (
        f"Start date : {itinerary_detail.start_date}\n",
        f"End date : {itinerary_detail.end_date}\n",
        f"perpose : {itinerary_detail.description}\n",
        f"travel_with : {itinerary_detail.travel_with}\n"
    )

async def run(mcp_server: MCPServer, itinerary_detail: ItineraryDetail):
   agent = Agent(
       name="Travel Planner Agent",
       instructions="You are travel planner, Use every functions to response the requirements.\n",
       model="gpt-4.1-mini",
       mcp_servers=[mcp_server],
       model_settings=ModelSettings(tool_choice="required", temperature=0.8),
       output_type=Schadule,
   )
   prompt = itinerary_detail_to_prompt(itinerary_detail)
   print(prompt)
   result = await Runner.run(agent, input=prompt)
   return result.final_output
