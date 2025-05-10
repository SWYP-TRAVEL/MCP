import random
import requests
import xml.etree.ElementTree as et
from typing import List, Optional
from enum import Enum


# api_key = "TDgGr/x6dfrWnIXejJ3/YbDRGmYcayi0vK2sywGSahP8zsQlkojKZwkcBQU2bsYre5aP6y1YaLFnXhEKxzGqmg=="
api_key = "U+A0efX1x7HoUpPkcQjWQNStDB4ReZkO+G6RRfwo71N8xefvkeG4i3qq8kT7pGyzs3o9RtIclCa2alethJRAnw=="
region_url = "http://apis.data.go.kr/B551011/KorService1/areaBasedList1"
around_url = "http://apis.data.go.kr/B551011/KorService1/locationBasedList1"
keyword_url   = "http://apis.data.go.kr/B551011/KorService1/searchKeyword1"

class TourDto:
    def __init__(self, title, first_image, addr1, mapx, mapy, contentid):
        self.title = title  #여행지 이름
        self.first_image = first_image  #여행지 사진
        self.addr1 = addr1  #여행지 주소
        self.mapx = mapx  #경도
        self.mapy = mapy  #위도
        self.contentid = contentid
    def __repr__(self):
        return (
            f"content id: {self.contentid}\n"
            f"place name: {self.title}\n"
            f"image URL: {self.first_image}\n"
            f"address: {self.addr1}\n"
            f"mapX: {self.mapx}\n"
            f"mapY: {self.mapy}\n"
        )

class AttractionType(str, Enum):
    tourist_spot = "12",
    # cultural_activities = "14",
    leisure_sports = "28",
    shopping = "38",
    restaurant = "39"

class AreaEnum(str, Enum):
   전국 =  "0"
   서울시 = "1"
   인천시 = "2"
   대전시 = "3"
   대구시 = "4"
   광주시 = "5"
   부산시 = "6"
   울산시 = "7"
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

def list_attractions_by_region(attraction_type: AttractionType = AttractionType.tourist_spot,
                              region: AreaEnum = AreaEnum.전국) -> list[TourDto]:
    """
    Returns a list of attractions filtered by category and geographic region.
    
    This function retrieves attractions based on specified category and region,
    providing a curated selection of places to visit.
    
    Args:
        attraction_type (AttractionType): Category of attractions to find:
            - tourist_spots (12): Tourist attractions (landmarks, scenic spots)
            - leisure_sports (28): Leisure and sports activities
            - shopping (38): Shopping destinations
            - restaurant (39): restaurant destinations
        region (AreaEnum): Geographic region to search within:
            - 전국 (All regions - nationwide search)
            - 서울, 부산, 대구, etc. (Specific cities or provinces)
    
    Returns:
        list[TourDto]: A list of attraction information objects (maximum 15 items)
    
    Example:
        list_attractions_by_region(AttractionType.tourist_spots, AreaEnum.서울)
    """
    region_str: str = ""
    if region != AreaEnum.전국:
        region_str = region.value
    region_params = {
        'MobileOS': 'ETC',  # Required
        'MobileApp': 'AppTest',  # Required
        "ServiceKey": api_key,  # API key
        # "contentTypeId": attraction_type.value,
        "arrange": "Q",
        # "areaCode": region_str,  # Geographic region code
        "numOfRows": 25,  # Results per page
        "pageNo": 1  # Page number (sorted by name)
    }
    response = requests.get(region_url, params=region_params)
    # Currently returns first few results; planned to implement random selection in the future
    dtos = extract_xml_data(response.text)
    return random.sample(dtos, 5)

def find_nearby_attractions(mapX=127.0317056, mapY=37.289984, attraction_type: AttractionType = AttractionType.tourist_spot) ->  Optional[List[TourDto]]:
    """
    Returns a list of recommended attractions near a specific location based on coordinates and type.
    
    Args:
        mapX (float): The longitude coordinate (east-west position) of the center location
        mapY (float): The latitude coordinate (north-south position) of the center location
        attraction_type (TourType): The category of attractions to find:
            - cultural_activities (14): Cultural facilities
            - tourist_spots (12): Tourist attractions
            - festivals (15): Festivals, performances, events
            - travel_courses (25): Travel routes
            - leisure_sports (28): Leisure and sports activities
            - shopping (38): Shopping destinations
        
    Returns:
        list[TourDto]: A list of nearby attraction information objects within 2000m of the specified coordinates
    
    Example:
        find_nearby_attractions("126.9816", "37.5640", TourType.tourist_spots)
    """
    around_params = {
        'MobileOS': 'ETC',  #필수
        'MobileApp': 'AppTest',  #필수
        "ServiceKey": api_key,  #api key
        "contentTypeId": attraction_type.value,  #관광타입
        "numOfRows": 50,  #한페이지당 보여질 개수
        "pageNo": 1,  #몇번째 페이지인지(이름순으로 정렬되어있음)
        "mapX": str(mapX),  #경도
        "mapY": str(mapY),  #위도
        "radius": 2000  #위치로부터 몇m까지인지(최대2000m)
    }
    response = requests.get(around_url, params=around_params)

    dtos = extract_xml_data(response.text)
    print(response.text)
    if len(dtos) > 5:
        return random.sample(dtos, 5)
    else:
        return dtos

async def search_attractions_by_keyword(
    keyword: str, 
    attraction_type: AttractionType = AttractionType.tourist_spot, 
    region: AreaEnum = AreaEnum.전국, 
    page_number: int = 1) -> List[TourDto] | None:
    """
    Searches for attractions based on a keyword with optional filtering by type and region.
    
    Args:
        keyword (str): The search term(one word) to find matching attractions (e.g., "palace", "museum")
        attraction_type (TourType): Category of attractions to search within:
            - cultural_activities (14): Cultural facilities
            - tourist_spots (12): Tourist attractions
            - festivals (15): Festivals, performances, events
            - travel_courses (25): Travel routes
            - leisure_sports (28): Leisure and sports activities
            - shopping (38): Shopping destinations
        region: AreaEnum = Field(default=AreaEnum.전국, description="Geographic region to limit the search to"), 
        page_number (int): Page number for paginated results (starts from 1)
    
    Returns:
        List[TourDto]: A list of attractions matching the keyword and filters (maximum 15 items per page)
    
    Example:
        search_attractions_by_keyword("palace", TourType.tourist_spots, AreaEnum.서울)
    """
    region_str: str = ""
    if region != AreaEnum.전국:
        region_str = region.value

    search_params = {
        'MobileOS': 'ETC',  # Required
        'MobileApp': 'AppTest',  # Required
        "ServiceKey": api_key,  # API key
        # "contentTypeId": attraction_type.value,  # Attraction category
        # "areaCode": region_str,  # Geographic region code
        "keyword": keyword,  # URL-encoded search term
        "arrange" : "Q",
        "numOfRows": 100,  # Results per page
        "pageNo": page_number  # Page number
    }
    
    response = requests.get(keyword_url, params=search_params)
    if response.text:
        print(response.content)
        dtos = extract_xml_data(response.text)
        return random.sample(dtos, 5)
    else:
        return "not found"

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
        content_id = item.find("contentid").text if item.find("contentid") is not None else "N/A"
        # ItemDTO 객체 생성 후 리스트에 추가
        dto = TourDto(title, first_image, addr1, mapx, mapy, content_id)
        dtos.append(dto)
    return dtos
