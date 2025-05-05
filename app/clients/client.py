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

class Triplet(BaseModel):
    area1_name:str
    area1_travel_theme: str
    area2_name:str
    area2_travel_theme: str
    area3_name:str
    area3_travel_theme: str

def itinerary_detail_to_prompt(itinerary_detail: ItineraryDetail) -> str:
    prompt = (
        f"Start date : {itinerary_detail.start_date}\n"
        f"End date : {itinerary_detail.end_date}\n"
        f"travel_with : {itinerary_detail.travel_with}\n"
        f"perpose : {itinerary_detail.description}\n"
    )
    if itinerary_detail['theme']:
        prompt += f"travel theme : {itinerary_detail.theme}"
    return prompt

async def run(mcp_server:MCPServerSse, itinerary_detail: ItineraryDetail):
    agent = Agent(
       name="Travel Planner Agent",
       instructions="You are Korean travel planner, Use **all** functions to response the requirements.\n",
       model="o4-mini-2025-04-16",
       mcp_servers=[mcp_server],
       model_settings=ModelSettings(tool_choice="required"),
       output_type=ResponseFormat,
   )
    prompt = itinerary_detail_to_prompt(itinerary_detail) 
    prompt += "특정 지역에서 확장하는 형태로, 전체 여행 일정을 만들어주세요!"
    print(prompt)
    result = await Runner.run(agent, input=prompt)
    return result.final_output


async def triplet(mcp_server: MCPServerSse, itinerary_detail: ItineraryDetail):
    agent = Agent(
        name="recommand travel theme",
        # instructions="Entroduce 3 specific location for the and explain the thmem",
        model='gpt-4.1-mini',
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(
            tool_choice="search_attractions_by_keyword",
            temperature=0.3
            # reasoning={"effort": "low"}
        ),
        output_type=Triplet
    )
    prompt = itinerary_detail_to_prompt(itinerary_detail)
    prompt += (
        "먼저 여행지에 어울리는 area 3곳을 선택하세요.\n"
        "- thmem은 30자 이내의 소개문구를 작성해주세요.\n"
        "- area 이름은 \"xx시 xx구\" 혹은 \"xx도 xx시\" 입니다.\n"
        "- 계속 찾고싶다면 `page_number`를 변경하세요."
    )
    print(prompt)
    result = await Runner.run(agent, input=prompt)
    print(result.final_output)
    return result.final_output