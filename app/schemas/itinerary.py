"""
Itinerary schemas for API request/response models.
"""
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from typing import Annotated

class TravelWith(str, Enum):
    alone   = "alone"
    friends = "friends"
    family  = "family"
    lover   = "lover"

class ItineraryDetail(BaseModel):
    travel_with: TravelWith
    duration: Annotated[int, "Travel duration in days"]
    description: str
    theme: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def __str__(self):
        # 한국어 문맥에 맞게 travel_with 값에 따라 다른 표현 사용
        if self.travel_with.value == "alone":
            companion_text = "혼자서"
        else:
            companion_text = {
                "friends": "친구들과",
                "family": "가족과",
                "lover": "연인과"
            }.get(self.travel_with.value, f"{self.travel_with.value}와")
        
        theme_info = f", 여행 테마: {self.theme}" if self.theme else ""
        
        return (
            f"{self.duration}일간,\n"
            f"{companion_text}{theme_info}: {self.description}\n"
            f"current location (longitude : {self.longitude}, latitude: {self.latitude})\n"
        )