from agents.mcp import MCPServerSse
from schemas.itinerary import ThemeFormat
from agents import Agent, Runner, ModelSettings
from pydantic import BaseModel, Field

INSTRUCTION = """당신은 여행지 추천 전문가입니다.
tool을 3번 내외로 호출하여 사용자에게 여행지를 추천하세요.

## Instruction
- 서로 다른 특성을 가진 3곳의 구체적인 도시나 지역(시/도 단위)을 여행지로 추천하세요.
- 지역을 특정하기 어렵다면 전국을 선택하세요.
- 각 여행지에 대한 간결하고 매력적인 설명을 제공하세요.
- 여행지 설명은 30단어 내외로 간결하게 작성하세요.
- 추천 지역은 반드시 구체적인 행정구역명(예: 경기도 광주시, 대전광역시, 서울특별시)으로 작성하세요.
"""


model_name = "gpt-4.1-mini"

model_settings = ModelSettings(
    tool_choice="search_attractions_by_keyword",
    temperature=0.2,
)


class Destination(BaseModel):
    location: str = Field(description="구체적인 행정구역명 (예: 경기도 광주시, 대전광역시, 서울특별시)")
    theme: str = Field(description="해당 지역의 여행 테마")
    address: str = Field(description="해당 지역의 정확한 주소")
    image_url: str = Field(description="해당 지역 이미지 url의 경로")
    mapx: float = Field(description="해당 지역의 위도")
    mapy: float = Field(description="해당 지역의 경도")

class TravelRecommendations(BaseModel):
    recommendation1: Destination
    recommendation2: Destination
    recommendation3: Destination

async def triplet_manager(mcp_server: MCPServerSse, theme: ThemeFormat):
    agent = Agent(
        model=model_name,
        model_settings=model_settings,
        name="Triplet manager",
        instructions=INSTRUCTION,
        mcp_servers=[mcp_server],
        output_type=TravelRecommendations
    )
    prompt = str(theme.dict(exclude_none=True)) + "\n위 내용에 어울리는 여행지 3곳을 추천해주세요."
    print(prompt)
    result = await Runner.run(agent, input=prompt)
    print(result.final_output)
    return result.final_output
