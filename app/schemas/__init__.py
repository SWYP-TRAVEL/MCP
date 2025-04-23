"""
Schemas module for API request/response Pydantic models.
"""

from .base import BaseResponse, PaginatedResponse
from .itinerary import ItineraryDetail, TravelWith
from .common import StatusEnum, ErrorResponse, HealthCheck

__all__ = [
    'BaseResponse',
    'PaginatedResponse',
    'ItineraryDetail',
    'TravelWith',
    'StatusEnum',
    'ErrorResponse',
    'HealthCheck',
]