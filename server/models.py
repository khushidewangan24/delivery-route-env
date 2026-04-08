"""Pydantic models for request/response validation"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class DeliveryLocation(BaseModel):
    """Represents a delivery location"""
    id: str
    lat: float
    lon: float
    weight: float  # Package weight in kg
    time_window_start: float  # Minutes from start
    time_window_end: float  # Minutes from start
    priority: int = Field(1, ge=1, le=5)  # 1-5 priority level


class ResetRequest(BaseModel):
    """Request body for /reset endpoint"""
    session_id: Optional[str] = None
    difficulty: Optional[str] = "medium"
    seed: Optional[int] = None


class StepRequest(BaseModel):
    """Request body for /step endpoint"""
    session_id: str
    action: int
    

class StateRequest(BaseModel):
    """Request body for /state endpoint"""
    session_id: str


class EnvironmentResponse(BaseModel):
    """Standard response format"""
    session_id: str
    observation: Dict[str, Any]
    reward: float = 0.0
    terminated: bool = False
    truncated: bool = False
    info: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    active_sessions: int = 0