"""
Base schemas that can be reused across the application.
"""
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List, Dict, Any
from datetime import datetime

T = TypeVar('T')

class BaseResponse(BaseModel):
    """Base response model that API endpoints can inherit from"""
    success: bool = True
    message: Optional[str] = None

class PaginatedResponse(BaseResponse, Generic[T]):
    """Paginated response model for list endpoints"""
    total: int
    page: int
    size: int 
    items: List[T]