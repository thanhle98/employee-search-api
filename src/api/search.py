from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from src.models import StatusEnum
from src.database import db

router = APIRouter(prefix="/api/v1", tags=["search"])

@router.get("/employees/search")
async def search_employees(
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    department: Optional[str] = Query(None, description="Filter by department"),
    position: Optional[str] = Query(None, description="Filter by position"),
    location: Optional[str] = Query(None, description="Filter by location"),
    status: Optional[StatusEnum] = Query(None, description="Filter by status"),
    limit: Optional[int] = Query(50, ge=1, le=200, description="Number of results to return"),
    offset: Optional[int] = Query(0, ge=0, description="Number of results to skip"),
    select: Optional[str] = Query(None, description="Select fields to return (comma-separated list of valid fields: id, first_name, last_name, email, phone, department, position, location, status). If not specified, all fields are returned.")
):
    """
    Search employees with various filters.
    
    - **first_name**: Search in employee first names (partial match)
    - **last_name**: Search in employee last names (partial match)
    - **department**: Filter by department (partial match)
    - **position**: Filter by position (partial match)
    - **location**: Filter by location (partial match)
    - **status**: Filter by exact status (ACTIVE, INACTIVE, TERMINATED)
    - **limit**: Maximum number of results to return (1-200)
    - **offset**: Number of results to skip for pagination
    - **select**: Select fields to return (comma-separated list of valid fields: id, first_name, last_name, email, phone, department, position, location, status)
    """
    
    filters = {
        "first_name": first_name,
        "last_name": last_name,
        "department": department,
        "position": position,
        "location": location,
        "status": status,
        "limit": limit,
        "offset": offset
    }
    
    try:
        employees, total = db.search_employees(filters, select)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        "employees": employees,
        "total": total,
        "limit": limit or 50,
        "offset": offset or 0
    }