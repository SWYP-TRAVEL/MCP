"""
Common schemas that can be used throughout the application.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class StatusEnum(str, Enum):
    """Common status values for resources"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    DELETED = "deleted"

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    status_code: int
    path: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthCheck(BaseModel):
    """API health check response"""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
