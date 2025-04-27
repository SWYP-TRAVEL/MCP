from mcp.server.fastmcp import FastMCP
import requests
import xml.etree.ElementTree as et

mcp = FastMCP(name="mcp_server", port=8070, host="localhost")

api_key = "TDgGr/x6dfrWnIXejJ3/YbDRGmYcayi0vK2sywGSahP8zsQlkojKZwkcBQU2bsYre5aP6y1YaLFnXhEKxzGqmg=="
region_url = "http://apis.data.go.kr/B551011/KorService1/areaBasedList1"
around_url = "http://apis.data.go.kr/B551011/KorService1/locationBasedList1"

ex_tour_cat3 = [
    {"name": "국립공원", "value": "A01010100"},
    {"name": "계곡", "value": "A01010900"},
    {"name": "호수", "value": "A01011700"},
    {"name": "가족코스", "value": "C01120001"}
]
tour_type = [
    {"name": "관광지", "value": "12"},
    {"name": "문화시설", "value": "14"},
    {"name": "축제공연행사", "value": "15"},
    {"name": "여행코스", "value": "25"},
    {"name": "레포츠", "value": "28"},
    {"name": "쇼핑", "value": "38"}
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
def get_tour_types():
    """
    관광 타입 리스트 반환
    """
    return tour_type


@mcp.tool()
def get_spot_list(type_id="12", cat1="", cat2="", cat3="A01010100") -> list[TourDto]:
    """
    추천 여행 타입에 따른 여행지 리스트 전달.
    """
    region_params = {
        'MobileOS': 'ETC',  #필수
        'MobileApp': 'AppTest',  #필수
        "ServiceKey": api_key,  #api key
        "contentTypeId": type_id,  #관광타입  / 12: 관광지, 14: 문화시설 ....
        "cat1": cat1,  #대분류 코드
        "cat2": cat2,  #중분류 코드
        "cat3": cat3,  #소분류 코드
        "numOfRows": 3,  #한페이지당 보여질 개수
        "pageNo": 1  #몇번째 페이지인지(이름순으로 정렬되어있음)
    }
    response = requests.get(region_url, params=region_params)
    return extract_xml_data(response.text)  #지금은 맨앞 3개만 받아오는데 나중에 랜덤으로 바꿀예정


@mcp.tool()
def get_around_list(longitude="127.0317056", latitude="37.289984", type_id="12") -> list[TourDto]:
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
