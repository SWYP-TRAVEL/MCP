from typing import List, Literal
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from schemas.itinerary import ItineraryDetail
from agents import Agent, Runner, ModelSettings, RunResult, ToolCallOutputItem
from agents.mcp import MCPServerSse

@dataclass
class Coordinate:
    latitude: str = Field(alias="mapX")
    longitude: str = Field(alias="mapY")

@dataclass
class SpotInfo:
    content_id: str
    content_name: str
    address: str
    image_url: str
    oneline_describe: str
    mapx: float
    mapy: float

class DailySchedule(BaseModel):
    day: int
    breakfast_info: SpotInfo
    lunch_info: SpotInfo
    dinner_info: SpotInfo
    attraction1_info: SpotInfo
    attraction2_info: SpotInfo

class MCPResponseFormat(BaseModel):
    travel_title: str
    travel_days: int
    itinerary: List[DailySchedule]

class Spot_DTO(BaseModel):
    attraction_type: Literal["breakfast", "lunch", "dinner", "attraction1", "attraction2"]
    name: str
    address: str
    description: str
    image_url: str
    mapx: float
    mapy: float

class ResponseDailySchedule(BaseModel):
    day: int
    breakfast_info: Spot_DTO
    lunch_info: Spot_DTO
    dinner_info: Spot_DTO
    attraction1_info: Spot_DTO
    attraction2_info: Spot_DTO

class ResponseFormat(BaseModel):
    title: str
    travel_days: int
    itnerary: List[ResponseDailySchedule]
        
INSTRUCTION = (
    "당신은 한국 여행 계획 전문가입니다.\n\n"
    "사용자가 요청한 특정 지역(좌표로 제공. latitude 와 longitude) 에 대한 여행 일정을 작성해주세요.\n\n"
    "각 일정에는 다음 정보가 포함되어야 합니다:\n"
    "- 아침 식사 장소 [정확한 content_id, content_name,  한 줄 설명]\n"
    "- 점심 식사 장소 [정확한 content_id, content_name,  한 줄 설명]\n"
    "- 저녁 식사 장소 [정확한 content_id, content_name,  한 줄 설명]\n"
    "- 관광지 1 [정확한 content_id, content_name,  한 줄 설명]\n"
    "- 관광지 2 [정확한 content_id, content_name,  한 줄 설명]\n\n"
    "모든 장소는 반드시 tool을 사용하여 실제 존재하는 장소의 정보를 조회해야 합니다.\n"
    "tool을 통해 각 장소의 content_name(place name), `content_id`을 정확히 가져오세요.\n"
    "응답은 항상 한국어로 작성하고, 최종 결과는 ResponseFormat 형식에 맞게 구조화하세요.\n"
    "사용자의 여행 일수에 맞춰 전체 일정을 일별로 구성해주세요."
    "초반(1,2회)에는 `find_nearby_attractions` 쓰지만, 그이후는 `list_attractions_by_region`를 쓰는게 좋습니다"
)




import json
def parse_place_info(text):
    """
    장소 정보 텍스트를 파싱하여 딕셔너리로 반환하는 함수
    
    Args:
        text (str): 장소 정보 텍스트
    
    Returns:
        dict: 파싱된 장소 정보 딕셔너리
    """
    place_info = {}
    for line in text.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            place_info[key.strip()] = value.strip()
    
    return place_info

async def create_itinerary(mcp_server: MCPServerSse, itinerary: ItineraryDetail):
    model_name = "gpt-4.1"

    model_settings = ModelSettings(
        tool_choice="required",
        temperature=0.7,
    )

    agent = Agent(
        model=model_name,
        model_settings=model_settings,
        name="Journey planner",
        instructions=INSTRUCTION,
        mcp_servers=[mcp_server],
        output_type=MCPResponseFormat
    )
    
    prompt = """tool은 5번정도 사용해서 되도록이면 중복추천을 제외하고.
그 tool의 결과에만 기반해서 여행지를 추천해주세요.
""" + str(itinerary) 
    result: RunResult = await Runner.run(agent, input=prompt)
    print(result)
    places_dict = {}
    
    for item in result.new_items:
        if isinstance(item, ToolCallOutputItem):
            if item.output:
                try:
                    # 디버깅을 위해 raw 출력 확인
                    print(f"Raw output: {item.output}")
                    
                    # JSON 파싱 시도
                    outputs = json.loads(item.output)
                    print(outputs)
                    
                    # 이전 코드와 같이 outputs 처리
                    for out in outputs:
                        print(out)
                        if isinstance(out, dict) and 'text' in out:
                            text = out['text']
                        else:
                            text = str(out)
                        
                        place_info = parse_place_info(text)
                        if 'content id' in place_info:
                            places_dict[place_info['content id']] = place_info
                
                except json.JSONDecodeError:
                    # JSON 파싱 실패 시 직접 텍스트로 처리
                    print(f"JSON parsing failed, treating as raw text: {item.output}")
                    text = item.output
                    place_info = parse_place_info(text)
                    if 'content id' in place_info:
                        places_dict[place_info['content id']] = place_info
        
    mcp_result: MCPResponseFormat = result.final_output
    
    # ResponseFormat 객체 생성
    response_format = ResponseFormat(
        title=mcp_result.travel_title,
        travel_days=mcp_result.travel_days,
        itnerary=[]  # 참고: ResponseFormat 클래스의 오타 (itnerary)를 그대로 사용
    )
    
    # 각 DailySchedule을 ResponseDailySchedule로 변환
    for sched in mcp_result.itinerary:
        response_daily = ResponseDailySchedule(
            day=sched.day,
            breakfast_info=create_spot_dto("breakfast", sched.breakfast_info, places_dict),
            lunch_info=create_spot_dto("lunch", sched.lunch_info, places_dict),
            dinner_info=create_spot_dto("dinner", sched.dinner_info, places_dict),
            attraction1_info=create_spot_dto("attraction1", sched.attraction1_info, places_dict),
            attraction2_info=create_spot_dto("attraction2", sched.attraction2_info, places_dict)
        )
        response_format.itnerary.append(response_daily)
    
    print(response_format)
    # 디버깅용 출력 (필요시 유지)
    return response_format

async def create_suggestion(input: str):
    model_name = "gpt-4.1-mini"

    model_settings = ModelSettings(
        tool_choice="none",
        temperature=1,
    )
    agent = Agent(
        model=model_name,
        model_settings=model_settings,
        name="Suggestion",
    )
    prompt = """당신은 여행 서비스의 입력 필드에 표시될 플레이스홀더 텍스트를 생성해야 합니다. 사용자가 "어떤 여행을 꿈꾸고 계신가요?"라는 질문을 받았을 때 어떻게 답변할지 예시를 제공하세요.

다음 조건을 따라 플레이스홀더 텍스트를 작성하세요:
1. 다양한 여행 스타일(힐링, 모험, 문화체험, 자연 감상 등)을 반영하는 **1**개의 예시 문장을 작성하세요
2. 현재 기분이나  활동에 대한 선호도를 표현하는 자연스러운 대화체로 작성하세요
3. "~하고 싶어요", "~면 좋겠어요" 등의 소망/희망 표현을 사용하세요
4. 전체 길이는 30자 내외로 작성하세요. 
5. 한국어로 작성하세요
6. 구체적 지역을 언급하지 마세요.[금지어]

<example>
요즘 지겨워서 조용하고 힐링되는 여행이었으면 좋겠어요.
</example>
    """
    prompt += "\n사용자가 현재까지 입력한 내용은 다음과 같습니다.\n"+input
    result = await Runner.run(agent, prompt)
    return result.final_output

async def change_attraction(mcp_server: MCPServerSse, mapX, mapY):
    model_name = "gpt-4.1-mini"

    model_settings = ModelSettings(
        tool_choice="auto",
        temperature=0.53,
    )
    agent = Agent(
        model=model_name,
        model_settings=model_settings,
        name="Journey planner",
        mcp_servers=[mcp_server],
        output_type=Spot_DTO
    )
    prompt = f"다음 좌표 주변의 관광지를 찾아주세요. mapX: {mapX}, mapY: {mapY}"
    
    # 에이전트를 실행하여 주변 관광지 검색
    result: RunResult = await Runner.run(agent, input=prompt)
    print(result.final_output)
    return result.final_output

def create_spot_dto(attraction_type: str, spot_info: SpotInfo, places_dict: dict) -> Spot_DTO:
    """
    SpotInfo 객체와 places_dict의 추가 정보를 사용하여 Spot_DTO 객체 생성
    """
    # 해당 place_id에 대한 정보 가져오기
    place_data = places_dict.get(spot_info.content_id, {})
    
    return Spot_DTO(
        attraction_type=attraction_type,
        name=spot_info.content_name,
        address=spot_info.address,
        description=spot_info.oneline_describe,
        image_url=spot_info.image_url,
        mapx=spot_info.mapx,
        mapy=spot_info.mapy
    )
