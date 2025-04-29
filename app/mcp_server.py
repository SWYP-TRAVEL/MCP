from mcp.server.fastmcp import FastMCP
import requests
import xml.etree.ElementTree as et
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

mcp = FastMCP(name="mcp_server", port=8070, host="localhost")

api_key = "TDgGr/x6dfrWnIXejJ3/YbDRGmYcayi0vK2sywGSahP8zsQlkojKZwkcBQU2bsYre5aP6y1YaLFnXhEKxzGqmg=="
region_url = "http://apis.data.go.kr/B551011/KorService1/areaBasedList1"
around_url = "http://apis.data.go.kr/B551011/KorService1/locationBasedList1"


class TourDto:
    def __init__(self, title, first_image, addr1, mapx, mapy):
        self.title = title  #여행지 이름
        self.first_image = first_image  #여행지 사진
        self.addr1 = addr1  #여행지 주소
        self.mapx = mapx  #경도
        self.mapy = mapy  #위도

    def __repr__(self):
        return (
            f"\n여행지 이름: {self.title}\n"
            f"사진 URL: {self.first_image}\n"
            f"주소: {self.addr1}\n"
            f"mapX: {self.mapx}\n"
            f"mapY: {self.mapy}\n"
        )


tour_type = [
    {"name": "관광지", "type_id": "12"},
    {"name": "문화시설", "type_id": "14"},
    {"name": "축제공연행사", "type_id": "15"},
    {"name": "여행코스", "type_id": "25"},
    {"name": "레포츠", "type_id": "28"},
    {"name": "쇼핑", "type_id": "38"}
]

class TourType(str, Enum):
    tourist_spot = "12",
    cultural_activities = "14",
    tour_course = "25",
    leisure_sports = "28",
    shopping = "38"

class AreaEnum(str, Enum):
   전체 = Field("", description="Use this field if there is no mention of a specific region.")
   서울 = "1"
   인천 = "2"
   대전 = "3"
   대구 = "4"
   광주 = "5"
   부산 = "6"
   울산 = "7"
   세종특별자치시 = "8"
   경기도 = "31"
   강원특별자치도 = "32"
   충청북도 = "33"
   충청남도 = "34"
   경상북도 = "35"
   경상남도 = "36"
   전북특별자치도 = "37"
   전라남도 = "38"
   제주도 = "39"

@mcp.tool()
def get_spot_list(tour_type: TourType=TourType.cultural_activities, area: AreaEnum=AreaEnum.전체) -> list[TourDto]:
    """
    1번만 사용할 수 있습니다.!!!
    지정된 여행 타입과 지역에 따른 여행지 목록을 반환합니다.
    """
    region_params = {
        'MobileOS': 'ETC',  #필수
        'MobileApp': 'AppTest',  #필수
        "ServiceKey": api_key,  #api key
        "contentTypeId": tour_type,  #관광타입  / 12: 관광지, 14: 문화시설 ....
        "areaCode": area,
        "numOfRows": 3,  #한페이지당 보여질 개수
        "pageNo": 1  #몇번째 페이지인지(이름순으로 정렬되어있음)
    }
    response = requests.get(region_url, params=region_params)
    print(response)
    return extract_xml_data(response.text)  #지금은 맨앞 3개만 받아오는데 나중에 랜덤으로 바꿀예정


@mcp.tool()
def get_around_list(mapX="127.0317056", mapY="37.289984", tour_type: TourType = TourType.cultural_activities) -> list[TourDto]:
    """
    특정 위치 주변의 여행지를 추천합니다.
    
    Args:
        mapX (str): 경도 좌표
        mapY (str): 위도 좌표
        type_id (TourType): 여행 타입 ID (12: 관광지, 14: 문화시설, 15: 축제공연행사, 25: 여행코스, 28: 레포츠, 38: 쇼핑)
        
    Returns:
        list[TourDto]: 주변 여행지 정보 목록
    """
    around_params = {
        'MobileOS': 'ETC',  #필수
        'MobileApp': 'AppTest',  #필수
        "ServiceKey": api_key,  #api key
        "contentTypeId": tour_type,  #관광타입  / 12: 관광지, 14: 문화시설 ....
        "numOfRows": 10,  #한페이지당 보여질 개수
        "pageNo": 1,  #몇번째 페이지인지(이름순으로 정렬되어있음)
        "mapX": mapX,  #경도
        "mapY": mapY,  #위도
        "radius": 2000  #위치로부터 몇m까지인지(최대2000m)
    }
    response = requests.get(around_url, params=around_params)
    return extract_xml_data(response.text)


def extract_xml_data(text) -> list[TourDto]:
    root = et.fromstring(text)

    # items 태그 안의 각 item 태그를 순회
    items = root.findall(".//item")

    # 추출할 데이터 리스트
    dtos = []

    for item in items:
        title = item.find("title").text if item.find("title") is not None else "N/A"
        first_image = item.find("firstimage").text if item.find("firstimage") is not None else "N/A"
        addr1 = item.find("addr1").text if item.find("addr1") is not None else "N/A"
        mapx = item.find("mapx").text if item.find("mapx") is not None else "N/A"
        mapy = item.find("mapy").text if item.find("mapy") is not None else "N/A"

        # ItemDTO 객체 생성 후 리스트에 추가
        dto = TourDto(title, first_image, addr1, mapx, mapy)
        dtos.append(dto)

    return dtos


if __name__ == "__main__":
    mcp.run(transport="sse")
