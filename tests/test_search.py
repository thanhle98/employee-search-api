import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.models import Employee, StatusEnum
from src.database import db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_data():
    """Setup test data before each test"""
    db.clear_all()
    
    # Add some test employees
    test_employees = [
        Employee(
            id="TEST001",
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            phone="+1-555-0001",
            department="Engineering",
            position="Software Developer",
            location="New York",
            status=StatusEnum.ACTIVE
        ),
        Employee(
            id="TEST002",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@test.com",
            phone="+1-555-0002",
            department="Marketing",
            position="Marketing Manager",
            location="London",
            status=StatusEnum.ACTIVE
        ),
        Employee(
            id="TEST003",
            first_name="Bob",
            last_name="Johnson",
            email="bob.johnson@test.com",
            department="Engineering",
            position="Senior Engineer",
            location="Singapore",
            status=StatusEnum.INACTIVE
        )
    ]
    
    for emp in test_employees:
        db.add_employee(emp)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Employee Search API is running"
    assert data["status"] == "healthy"

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_search_all_employees():
    """Test searching all employees without filters"""
    response = client.get("/api/v1/employees/search")
    assert response.status_code == 200
    
    data = response.json()
    assert "employees" in data
    assert "total" in data
    assert data["total"] == 3
    assert len(data["employees"]) == 3

def test_search_by_first_name():
    """Test searching employees by first name"""
    response = client.get("/api/v1/employees/search?first_name=John")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 1
    assert data["employees"][0]["first_name"] == "John"

def test_search_by_department():
    """Test searching employees by department"""
    response = client.get("/api/v1/employees/search?department=Engineering")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 2
    for emp in data["employees"]:
        assert "Engineering" in emp["department"]

def test_search_by_status():
    """Test searching employees by status"""
    response = client.get("/api/v1/employees/search?status=ACTIVE")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 2
    for emp in data["employees"]:
        assert emp["status"] == "ACTIVE"

def test_search_with_pagination():
    """Test searching with pagination"""
    response = client.get("/api/v1/employees/search?limit=1&offset=0")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 3
    assert len(data["employees"]) == 1
    assert data["limit"] == 1
    assert data["offset"] == 0

def test_search_no_results():
    """Test searching with filters that return no results"""
    response = client.get("/api/v1/employees/search?first_name=NonExistent")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 0
    assert len(data["employees"]) == 0

def test_select_valid_fields():
    """Test selecting valid fields"""
    response = client.get("/api/v1/employees/search?select=first_name,last_name,email")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 3
    # Verify only requested fields are present in response
    for emp in data["employees"]:
        assert "first_name" in emp
        assert "last_name" in emp  
        assert "email" in emp
        # These fields should not be present since they weren't selected
        assert "phone" not in emp or emp["phone"] is None
        assert "department" not in emp or emp["department"] is None

def test_sql_injection_prevention_invalid_field():
    """Test that invalid field names are rejected to prevent SQL injection"""
    # Try to inject SQL through select parameter
    malicious_select = "*, (SELECT password FROM users)"
    response = client.get(f"/api/v1/employees/search?select={malicious_select}")
    assert response.status_code == 400
    
    data = response.json()
    assert "Invalid field" in data["detail"]

def test_sql_injection_prevention_drop_table():
    """Test protection against DROP TABLE injection"""
    malicious_select = "* FROM employees; DROP TABLE employees; --"
    response = client.get(f"/api/v1/employees/search?select={malicious_select}")
    assert response.status_code == 400
    
    data = response.json()
    assert "Invalid field" in data["detail"]

def test_sql_injection_prevention_union_attack():
    """Test protection against UNION-based SQL injection"""
    malicious_select = "id UNION SELECT password FROM admin_users"
    response = client.get(f"/api/v1/employees/search?select={malicious_select}")
    assert response.status_code == 400
    
    data = response.json()
    assert "Invalid field" in data["detail"]

def test_sql_injection_prevention_semicolon():
    """Test protection against semicolon-based injection"""
    malicious_select = "id; DELETE FROM employees"
    response = client.get(f"/api/v1/employees/search?select={malicious_select}")
    assert response.status_code == 400
    
    data = response.json()
    assert "Invalid field" in data["detail"]

def test_field_validation_mixed_valid_invalid():
    """Test that requests with both valid and invalid fields are rejected"""
    mixed_select = "first_name,malicious_field,last_name"
    response = client.get(f"/api/v1/employees/search?select={mixed_select}")
    assert response.status_code == 400
    
    data = response.json()
    assert "Invalid field 'malicious_field'" in data["detail"]

def test_field_validation_case_sensitive():
    """Test that field validation is case-sensitive"""
    # These should fail because our whitelist is case-sensitive
    response = client.get("/api/v1/employees/search?select=FIRST_NAME,LAST_NAME")
    assert response.status_code == 400
    
    response = client.get("/api/v1/employees/search?select=First_Name")
    assert response.status_code == 400

def test_field_validation_with_spaces():
    """Test that fields with extra spaces are handled correctly"""
    response = client.get("/api/v1/employees/search?select= first_name , last_name , email ")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 3 