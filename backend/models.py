from pydantic import BaseModel, Field, validator
from typing import Literal, Optional
from datetime import datetime
from enum import Enum


class EscrowStatus(str, Enum):
    PENDING = "PENDING"
    LOCKED = "LOCKED"
    RELEASED = "RELEASED"
    DISPUTED = "DISPUTED"


class Milestone(BaseModel):
    id: str
    project_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    requirements: list[str] = Field(..., min_items=1)
    estimated_hours: int = Field(..., gt=0)
    status: EscrowStatus = EscrowStatus.PENDING
    escrow_amount: Optional[float] = Field(None, gt=0)
    created_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    deadline: Optional[str] = None
    submission_time: Optional[str] = None
    timeline_status: Optional[Literal["on-time", "late"]] = None
    
    @validator('requirements')
    def requirements_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('requirements list must not be empty')
        return v


class Project(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    milestones: list[Milestone] = []
    total_pfi: Optional[float] = Field(None, ge=0, le=100)


class InspectionResult(BaseModel):
    milestone_id: str
    passed: bool
    coverage_score: float = Field(..., ge=0, le=100)
    feedback: str = Field(..., min_length=1)
    missing_requirements: list[str] = []
    analyzed_at: datetime
    code_blob_hash: str


class PFISnapshot(BaseModel):
    timestamp: datetime
    pfi_score: float = Field(..., ge=0, le=100)
    project_id: str
    milestone_id: str


class UserReputation(BaseModel):
    user_id: str
    current_pfi: float = Field(..., ge=0, le=100)
    total_projects: int = Field(..., ge=0)
    successful_submissions: int = Field(..., ge=0)
    failed_submissions: int = Field(..., ge=0)
    average_coverage: float = Field(..., ge=0, le=100)
    reputation_history: list[PFISnapshot] = []
    updated_at: datetime


class PFIMetrics(BaseModel):
    performance_score: float = Field(..., ge=0, le=100)
    financial_score: float = Field(..., ge=0, le=100)
    combined_pfi: float = Field(..., ge=0, le=100)


# Auth Models
class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    role: Literal["client", "developer"]
    payment_threshold: Optional[float] = None  # developer only


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    user_id: str
    name: str
    email: str
    role: str
    payment_threshold: Optional[float] = None
    hourly_rate: Optional[float] = None


# API Request/Response Models
class PlanRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    user_id: str


class PlanResponse(BaseModel):
    project_id: str
    milestones: list[dict]


class SubmitResponse(BaseModel):
    passed: bool
    feedback: str
    pfi_score: Optional[float] = None
    reputation_change: Optional[dict] = None
