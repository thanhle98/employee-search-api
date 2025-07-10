from fastapi import APIRouter, Query, HTTPException, Depends, Response
from fastapi.responses import JSONResponse
from typing import Optional
from src.models import StatusEnum, EmployeeSearchParams, EmployeeSearchResponse, EmployeeResponse
from src.database import db

router = APIRouter(prefix="/api/v1", tags=["search"])

def get_search_params(
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    department: Optional[str] = Query(None, description="Filter by department"),
    position: Optional[str] = Query(None, description="Filter by position"),
    location: Optional[str] = Query(None, description="Filter by location"),
    status: Optional[StatusEnum] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    select: Optional[str] = Query(None, description="Select fields to return (comma-separated list of valid fields: id, first_name, last_name, email, phone, department, position, location, status). If not specified, all fields are returned.")
) -> EmployeeSearchParams:
    """Dependency to validate and parse search parameters using Pydantic"""
    return EmployeeSearchParams(
        first_name=first_name,
        last_name=last_name,
        department=department,
        position=position,
        location=location,
        status=status,
        limit=limit,
        offset=offset,
        select=select
    )

@router.get("/employees/search")
async def search_employees(
    params: EmployeeSearchParams = Depends(get_search_params)
):
    """
    Search employees with various filters using Pydantic validation.
    
    This endpoint provides comprehensive employee search functionality with:
    - **first_name**: Search in employee first names (case-insensitive partial match)
    - **last_name**: Search in employee last names (case-insensitive partial match)
    - **department**: Filter by department (case-insensitive partial match)
    - **position**: Filter by position (case-insensitive partial match)
    - **location**: Filter by location (case-insensitive partial match)
    - **status**: Filter by exact status (ACTIVE, INACTIVE, TERMINATED)
    - **limit**: Maximum number of results to return (1-200, default: 50)
    - **offset**: Number of results to skip for pagination (default: 0)
    - **select**: Comma-separated list of fields to return (optional)
    
    ### Field Selection:
    Valid fields for the `select` parameter: id, first_name, last_name, email, 
    phone, department, position, location, status
    
    ### Examples:
    - Search by name: `/employees/search?first_name=john&last_name=doe`
    - Filter by department: `/employees/search?department=engineering`
    - Pagination: `/employees/search?limit=20&offset=40`
    - Select specific fields: `/employees/search?select=id,first_name,last_name,email`
    - Combined filters: `/employees/search?department=sales&status=ACTIVE&limit=10`
    """
    
    # Convert Pydantic model to dict for database compatibility
    filters = {
        "first_name": params.first_name,
        "last_name": params.last_name,
        "department": params.department,
        "position": params.position,
        "location": params.location,
        "status": params.status,
        "limit": params.limit,
        "offset": params.offset
    }
    
    try:
        employees_data, total = db.search_employees(filters, params.select)
        
        if params.select:
            response_data = {
                "employees": employees_data,
                "total": total,
                "limit": params.limit,
                "offset": params.offset
            }
            return JSONResponse(content=response_data)
        else:
            employees = [EmployeeResponse(**emp_data) for emp_data in employees_data]
            
            response_data = {
                "employees": employees,
                "total": total,
                "limit": params.limit,
                "offset": params.offset
            }
            return JSONResponse(content=response_data)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")