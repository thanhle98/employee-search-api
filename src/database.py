import os
from typing import List, Optional, Tuple, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, func, or_, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from src.models import Employee, StatusEnum, Base

# Create database directory if it doesn't exist
DB_DIR = "data"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'employees.db')}"


class SQLAlchemyDatabase:
    def __init__(self):
        """Initialize database"""
        self.engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},  # Needed for SQLite
        )

        # Create sessionmaker
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    @contextmanager
    def get_session(self):
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _filter_employee_fields(
        self, employee_dict: dict, requested_fields: list
    ) -> dict:
        """Filter employee fields based on requested fields"""
        if not requested_fields or "*" in requested_fields:
            return employee_dict

        filtered_dict = {}
        for field in requested_fields:
            if field in employee_dict:
                filtered_dict[field] = employee_dict[field]

        return filtered_dict

    def _build_search_query(self, session: Session, filters: dict):
        """Build SQLAlchemy query based on filters"""
        query = session.query(Employee)

        conditions = []

        if filters.get("first_name"):
            conditions.append(Employee.first_name.ilike(f"%{filters['first_name']}%"))

        if filters.get("last_name"):
            conditions.append(Employee.last_name.ilike(f"%{filters['last_name']}%"))

        if filters.get("department"):
            conditions.append(Employee.department.ilike(f"%{filters['department']}%"))

        if filters.get("position"):
            conditions.append(Employee.position.ilike(f"%{filters['position']}%"))

        if filters.get("location"):
            conditions.append(Employee.location.ilike(f"%{filters['location']}%"))

        if filters.get("status"):
            conditions.append(Employee.status == filters["status"])

        if conditions:
            query = query.filter(and_(*conditions))

        return query

    def add_employee(self, employee_data: dict) -> Employee:
        """Add an employee to the database"""
        with self.get_session() as session:
            # Create employee with SQLAlchemy model
            employee = Employee(
                id=employee_data.get("id"),
                first_name=employee_data["first_name"],
                last_name=employee_data["last_name"],
                email=employee_data.get("email"),
                phone=employee_data.get("phone"),
                department=employee_data.get("department"),
                position=employee_data.get("position"),
                location=employee_data.get("location"),
                status=employee_data.get("status", StatusEnum.ACTIVE.value),
            )

            session.add(employee)
            session.flush()  # Flush to get the ID
            return employee

    def search_employees(
        self, filters: dict, select: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        """Search employees based on filters"""
        try:
            with self.get_session() as session:
                # Build the base query
                query = self._build_search_query(session, filters)

                # Get total count before pagination
                total = query.count()

                # Apply pagination
                offset = filters.get("offset", 0)
                limit = filters.get("limit", 50)

                # Execute query with pagination
                employees = query.offset(offset).limit(limit).all()

                # Convert to dictionaries
                employee_dicts = []
                for emp in employees:
                    emp_dict = {
                        "id": emp.id,
                        "first_name": emp.first_name,
                        "last_name": emp.last_name,
                        "email": emp.email,
                        "phone": emp.phone,
                        "department": emp.department,
                        "position": emp.position,
                        "location": emp.location,
                        "status": emp.status,
                    }
                    employee_dicts.append(emp_dict)

                # Handle field selection
                if select:
                    # Validate and parse select fields
                    allowed_fields = {
                        "id",
                        "first_name",
                        "last_name",
                        "email",
                        "phone",
                        "department",
                        "position",
                        "location",
                        "status",
                    }

                    requested_fields = [field.strip() for field in select.split(",")]

                    for field in requested_fields:
                        if field not in allowed_fields:
                            raise ValueError(
                                f"Invalid field '{field}' in select parameter"
                            )

                    # Filter fields for each employee
                    filtered_employees = [
                        self._filter_employee_fields(emp_dict, requested_fields)
                        for emp_dict in employee_dicts
                    ]
                    return filtered_employees, total

                return employee_dicts, total

        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")

    def get_all_employees(self) -> List[dict]:
        """Get all employees"""
        try:
            with self.get_session() as session:
                employees = session.query(Employee).all()
                return [
                    {
                        "id": emp.id,
                        "first_name": emp.first_name,
                        "last_name": emp.last_name,
                        "email": emp.email,
                        "phone": emp.phone,
                        "department": emp.department,
                        "position": emp.position,
                        "location": emp.location,
                        "status": emp.status,
                    }
                    for emp in employees
                ]
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")

    def get_employee_by_id(self, employee_id: str) -> Optional[dict]:
        """Get a specific employee by ID"""
        try:
            with self.get_session() as session:
                employee = (
                    session.query(Employee).filter(Employee.id == employee_id).first()
                )
                if employee:
                    return {
                        "id": employee.id,
                        "first_name": employee.first_name,
                        "last_name": employee.last_name,
                        "email": employee.email,
                        "phone": employee.phone,
                        "department": employee.department,
                        "position": employee.position,
                        "location": employee.location,
                        "status": employee.status,
                    }
                return None
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")

    def clear_all(self):
        """Clear all employees (useful for testing)"""
        try:
            with self.get_session() as session:
                session.query(Employee).delete()
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")


# Global database instance
db = SQLAlchemyDatabase()
