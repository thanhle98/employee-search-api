import os
import sqlite3
from typing import List, Optional, Tuple
from src.models import Employee as EmployeeModel, StatusEnum

# Create database directory if it doesn't exist
DB_DIR = "data"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DATABASE_PATH = os.path.join(DB_DIR, "employees.db")

class SQLiteDatabase:
    def __init__(self):
        """Initialize database and create tables if they don't exist"""
        self._create_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Enable accessing columns by name
        return conn
    
    def _create_tables(self):
        """Create the employees table if it doesn't exist"""
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id TEXT PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    department TEXT,
                    position TEXT,
                    location TEXT,
                    status TEXT NOT NULL DEFAULT 'ACTIVE'
                )
            """)
            
            # Create indexes for better search performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_first_name ON employees(first_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_last_name ON employees(last_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_department ON employees(department)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_position ON employees(position)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_location ON employees(location)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON employees(status)")
            
            conn.commit()
        finally:
            conn.close()
    
    def _row_to_employee(self, row: sqlite3.Row) -> EmployeeModel:
        """Convert a database row to an Employee model"""
        return EmployeeModel(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"] if "email" in row.keys() else None,
            phone=row["phone"] if "phone" in row.keys() else None,
            department=row["department"] if "department" in row.keys() else None,
            position=row["position"] if "position" in row.keys() else None,
            location=row["location"] if "location" in row.keys() else None,
            status=StatusEnum(row["status"]) if "status" in row.keys() else StatusEnum.ACTIVE
        )
    
    def _filter_employee_fields(self, employee: EmployeeModel, requested_fields: list) -> dict:
        """Filter employee fields based on requested fields"""
        employee_dict = employee.to_dict()
        if not requested_fields or "*" in requested_fields:
            return employee_dict
        
        filtered_dict = {}
        for field in requested_fields:
            if field in employee_dict:
                filtered_dict[field] = employee_dict[field]
        return filtered_dict
    
    def add_employee(self, employee: EmployeeModel) -> EmployeeModel:
        """Add an employee to the database"""
        conn = self._get_connection()
        try:
            conn.execute("""
                INSERT INTO employees (id, first_name, last_name, email, phone, department, position, location, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                employee.id,
                employee.first_name,
                employee.last_name,
                employee.email,
                employee.phone,
                employee.department,
                employee.position,
                employee.location,
                employee.status.value
            ))
            conn.commit()
            return employee
        finally:
            conn.close()
    
    def search_employees(self, filters: dict, select: Optional[str] = None) -> Tuple[List[dict], int]:
        """Search employees based on filters"""
        conn = self._get_connection()
        try:
            # Build the WHERE clause and parameters
            where_conditions = []
            params = []
            
            if filters["first_name"]:
                where_conditions.append("first_name LIKE ?")
                params.append(f"%{filters['first_name']}%")
            
            if filters["last_name"]:
                where_conditions.append("last_name LIKE ?")
                params.append(f"%{filters['last_name']}%")
            
            if filters["department"]:
                where_conditions.append("department LIKE ?")
                params.append(f"%{filters['department']}%")
            
            if filters["position"]:
                where_conditions.append("position LIKE ?")
                params.append(f"%{filters['position']}%")
            
            if filters["location"]:
                where_conditions.append("location LIKE ?")
                params.append(f"%{filters['location']}%")
            
            if filters["status"]:
                where_conditions.append("status = ?")
                params.append(filters["status"].value)
            
            # Build the query
            base_query = "FROM employees"
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            # Get total count
            count_query = f"SELECT COUNT(*) {base_query}"
            cursor = conn.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # Get paginated results
            offset = filters["offset"] or 0
            limit = filters["limit"] or 50

            # SECURITY: Validate select fields against whitelist to prevent SQL injection
            allowed_fields = {
                "id", "first_name", "last_name", "email", "phone", 
                "department", "position", "location", "status"
            }
            
            requested_fields = []
            if select:
                # Parse and validate each field
                requested_fields = [field.strip() for field in select.split(",")]
                
                for field in requested_fields:
                    if field not in allowed_fields:
                        # Log the invalid field attempt or raise an error
                        raise ValueError(f"Invalid field '{field}' in select parameter")
            
            # Always include required fields in the query, then filter response
            required_fields = {"id", "first_name", "last_name"}
            fields_to_query = required_fields.copy()
            
            if requested_fields:
                # Add requested fields to query (they're already validated)
                fields_to_query.update(requested_fields)
            else:
                # If no specific fields requested, get all fields
                fields_to_query = allowed_fields
            
            fields_str = ", ".join(sorted(fields_to_query))
            
            select_query = f"SELECT {fields_str} {base_query} LIMIT ? OFFSET ?"
            cursor = conn.execute(select_query, params + [limit, offset])
            rows = cursor.fetchall()
            
            employees = [self._row_to_employee(row) for row in rows]
            
            # Filter results to only include requested fields
            if requested_fields:
                filtered_employees = [
                    self._filter_employee_fields(emp, requested_fields) 
                    for emp in employees
                ]
                return filtered_employees, total
            else:
                # Return full employee objects as dictionaries
                return [emp.to_dict() for emp in employees], total
            
        finally:
            conn.close()
    
    def get_all_employees(self) -> List[EmployeeModel]:
        """Get all employees"""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM employees")
            rows = cursor.fetchall()
            return [self._row_to_employee(row) for row in rows]
        finally:
            conn.close()
    
    def get_employee_by_id(self, employee_id: str) -> Optional[EmployeeModel]:
        """Get a specific employee by ID"""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_employee(row)
            return None
        finally:
            conn.close()
    
    def clear_all(self):
        """Clear all employees (useful for testing)"""
        conn = self._get_connection()
        try:
            conn.execute("DELETE FROM employees")
            conn.commit()
        finally:
            conn.close()

# Global database instance
db = SQLiteDatabase() 