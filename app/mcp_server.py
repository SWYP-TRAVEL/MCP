from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP
import requests
import xml.etree.ElementTree as et
import random

mcp = FastMCP(name="mcp_server", port=8000, host="localhost")

api_key = "TDgGr/x6dfrWnIXejJ3/YbDRGmYcayi0vK2sywGSahP8zsQlkojKZwkcBQU2bsYre5aP6y1YaLFnXhEKxzGqmg=="
region_url = "http://apis.data.go.kr/B551011/KorService1/areaBasedList1"
around_url = "http://apis.data.go.kr/B551011/KorService1/locationBasedList1"
tour_count_url = "https://api.visitkorea.or.kr/hub/getTourInfoCnt.do"
region_list_api_url = "https://api.visitkorea.or.kr/hub/getSigungu.do"
tour_type_list_url = "https://api.visitkorea.or.kr/api/getApiCategoryList.do"

tour_type = [
    {"name": "관광지", "value": "12"},
    {"name": "문화시설", "value": "14"},
    {"name": "축제공연행사", "value": "15"},
    {"name": "여행코스", "value": "25"},
    {"name": "레포츠", "value": "28"},
    {"name": "쇼핑", "value": "38"}
]

city_list = [
    {"name": "서울", "value": "1"},
    {"name": "인천", "value": "2"},
    {"name": "대전", "value": "3"},
    {"name": "대구", "value": "4"},
    {"name": "광주", "value": "5"},
    {"name": "부산", "value": "6"},
    {"name": "울산", "value": "7"},
    {"name": "세종", "value": "8"},
    {"name": "경기도", "value": "31"},
    {"name": "강원도", "value": "32"},
    {"name": "충청북도", "value": "33"},
    {"name": "충청남도", "value": "34"},
    {"name": "경상북도", "value": "35"},
    {"name": "경상남도", "value": "36"},
    {"name": "전라북도", "value": "37"},
    {"name": "전라남도", "value": "38"},
    {"name": "제주도", "value": "39"}
]


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
            f"경도: {self.mapx}\n"
            f"위도: {self.mapy}\n"
        )


@mcp.tool()
def get_tour_types_big():
    """
    관광 타입 리스트 반환
    """
    return tour_type


@mcp.tool()
def get_tour_types_small(tour_type_code="12"):
    """
    관광 타입 리스트(소분류) 반환
    """
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "langDiv": "kor",
        "contentTypeId": [tour_type_code],
    }
    response = requests.post(tour_type_list_url, headers=headers, json=data)
    result = [{"cat3": item["cat3"], "cat3Nm": item["cat3Nm"]} for item in response.json()]
    return result


@mcp.tool()
def get_city_list():
    """
    한국 지역 리스트(시/도) 반환
    """
    return city_list


@mcp.tool()
def get_county_list(region_id="1") -> list[dict[str, Any]]:
    """
    한국 지역 리스트(시/군/구) 반환
    """
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "langDiv": "kor",
        "areaCd": region_id,
        "div": "reset"
    }
    response = requests.post(region_list_api_url, headers=headers, json=data)
    result = [{"signguCd": item["signguCd"], "signguNm": item["signguNm"]} for item in response.json()]

    return result


@mcp.tool()
def get_spot_list(type_id="12", cat1="", cat2="", cat3="", city_code="1", county_code="3") -> list[TourDto]:
    """
    추천 여행 타입에 따른 여행지 리스트 전달.
    """
    count = get_count(city_code, county_code, type_id, cat1, cat2, cat3)

    return_value = []

    for i in range(0, 10):
        random_index = random.randint(0, count)
        region_params = {
            'MobileOS': 'ETC',  #필수
            'MobileApp': 'AppTest',  #필수
            "ServiceKey": api_key,  #api key
            "contentTypeId": [type_id],  #관광타입  / 12: 관광지, 14: 문화시설 ....
            "cat1": cat1,  #대분류 코드
            "cat2": cat2,  #중분류 코드
            "cat3": cat3,  #소분류 코드
            "numOfRows": 1,  #한페이지당 보여질 개수
            "areaCode": city_code,  #시/도 코드
            "sigunguCode": county_code, #시/군/구 코드
            "pageNo": random_index  #몇번째 페이지인지(이름순으로 정렬되어있음)
        }

        response = requests.get(region_url, params=region_params)
        return_value.append(extract_xml_data(response.text)[0])

    return return_value


@mcp.tool()
def get_around_list(longitude="127.0317056", latitude="37.289984", type_id="12", radius=2000) -> list[TourDto]:
    """
    경도, 위도를 받고 해당 위치 주변 추천 여행지 정보를 전달함.
    """
    around_params = {
        'MobileOS': 'ETC',  #필수
        'MobileApp': 'AppTest',  #필수
        "ServiceKey": api_key,  #api key
        "contentTypeId": type_id,  #관광타입  / 12: 관광지, 14: 문화시설 ....
        "numOfRows": 3,  #한페이지당 보여질 개수
        "pageNo": 1,  #몇번째 페이지인지(이름순으로 정렬되어있음)
        "mapX": longitude,  #경도
        "mapY": latitude,  #위도
        "radius": radius  #위치로부터 몇m까지인지(최대2000m)
    }
    response = requests.get(around_url, params=around_params)
    return extract_xml_data(response.text)


def get_count(city_code, county_code, tour_type_code, cat1, cat2, cat3):
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "areaCd": city_code,
        "signguCd": county_code,
        "contentTypeId": [tour_type_code],
        "cat1": cat1,
        "cat2": cat2,
        "cat3": cat3
    }
    response = requests.post(tour_count_url, headers=headers, json=data)
    return int(response.text)

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
    print(get_spot_list())
    mcp.run(transport="sse")
