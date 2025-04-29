import asyncio
from typing import List
from pydantic import BaseModel
from agents import Agent, Runner, ModelSettings
from agents.mcp import MCPServerSse
from typing import Optional
from schemas.itinerary import ItineraryDetail


class Schadule(BaseModel):
    day: int
    breakfast_online_summary: str
    launch: str
    launch_online_summary: str
    dinner: str
    dinner_online_summary: str
    attraction1: str
    attraction1_one_line_summary: str
    attraction1_image_url: Optional[str]
    attraction2: str
    attraction2_one_line_summary: str
    attraction1_image_url: Optional[str]

class ResponseFormat(BaseModel):
    city: str
    travel_days: int
    itinerary: List[Schadule]

def itinerary_detail_to_prompt(itinerary_detail: ItineraryDetail) -> str:
    return (
        f"Start date : {itinerary_detail.start_date}\n"
        f"End date : {itinerary_detail.end_date}\n"
        f"perpose : {itinerary_detail.description}\n"
        f"travel_with : {itinerary_detail.travel_with}\n"
        "특정 지역에서 확장하는 형태로, 전체 여행 일정을 만들어주세요!"
    )

async def run(mcp_server:MCPServerSse, itinerary_detail: ItineraryDetail):
    agent = Agent(
       name="Travel Planner Agent",
       instructions="You are Korean travel planner, Use **all** functions to response the requirements.\n",
       model="gpt-4.1",
       mcp_servers=[mcp_server],
       model_settings=ModelSettings(tool_choice="required", temperature=0.7),
       output_type=ResponseFormat,
   )
    prompt = itinerary_detail_to_prompt(itinerary_detail)
    print(prompt)
    result = await Runner.run(agent, input=prompt)
    return result.final_output

async def triplet(mcp_server: MCPServerSse, itinerary_detail: ItineraryDetail):
    agent = Agent(
        name="recommand travel theme",
        instructions="You are "
    )