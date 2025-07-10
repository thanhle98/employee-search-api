from typing import Optional, Union, Dict, Any
from enum import Enum
from datetime import date
from sqlalchemy import Column, String, Index, Date
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field, EmailStr, ConfigDict
import uuid

Base = declarative_base()

class StatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    TERMINATED = "TERMINATED"

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    department = Column(String, nullable=True, index=True)
    position = Column(String, nullable=True, index=True)
    location = Column(String, nullable=True, index=True)
    status = Column(String, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_name_full', 'first_name', 'last_name'),
        Index('idx_dept_position', 'department', 'position'),
        Index('idx_location_status', 'location', 'status'),
    )


class EmployeeSearchParams(BaseModel):
    """Request model for employee search parameters."""
    model_config = ConfigDict(use_enum_values=True)
    
    first_name: Optional[str] = Field(None, description="Filter by first name")
    last_name: Optional[str] = Field(None, description="Filter by last name")
    department: Optional[str] = Field(None, description="Filter by department")
    position: Optional[str] = Field(None, description="Filter by position")
    location: Optional[str] = Field(None, description="Filter by location")
    status: Optional[StatusEnum] = Field(None, description="Filter by status")
    limit: int = Field(50, ge=1, le=200, description="Number of results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    select: Optional[str] = Field(None, description="Select fields to return (comma-separated list of valid fields: id, first_name, last_name, email, phone, department, position, location, status). If not specified, all fields are returned.")

class EmployeeResponse(BaseModel):
    """Response model for employee data."""
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
    
    id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    status: Optional[StatusEnum] = None

class EmployeeSearchResponse(BaseModel):
    """Response model for employee search results."""
    employees: Union[list[EmployeeResponse], list[Dict[str, Any]]] = []
    total: int
    limit: int
    offset: int
