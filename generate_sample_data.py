#!/usr/bin/env python3
"""
Script to generate sample HR database with mock employee data.
This script populates the mock database with realistic employee data.
"""

import random
import time

from src.models import Employee, StatusEnum
from src.database import db

# Sample data lists based on the screenshot and common HR data
FIRST_NAMES = [
    "005Test", "007Test", "Amelia", "Amanda", "AnaTest", "Arlani", 
    "John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", 
    "Emily", "James", "Jessica", "William", "Ashley", "Richard", 
    "Jennifer", "Thomas", "Amanda", "Christopher", "Stephanie",
    "Daniel", "Nicole", "Matthew", "Rachel", "Anthony", "Samantha"
]

LAST_NAMES = [
    "005", "007", "last", "Cerny", "Profile", "Sosala", "zxc",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", 
    "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", 
    "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", 
    "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson"
]

DEPARTMENTS = [
    "asd", "Engineering", "Marketing", "Sales", "Human Resources", 
    "Finance", "Operations", "Product", "Design", "Legal", 
    "Customer Support", "Research", "Quality Assurance", 
    "Business Development", "IT", "Procurement"
]

POSITIONS = [
    "Assistant Manager", "Software Developer", "Senior Engineer", 
    "Product Manager", "Designer", "Sales Representative", 
    "HR Specialist", "Financial Analyst", "Operations Manager", 
    "Marketing Coordinator", "Customer Success Manager", 
    "Data Analyst", "Project Manager", "Technical Lead", 
    "Business Analyst", "Quality Engineer", "DevOps Engineer"
]

LOCATIONS = [
    "Singapore", "Owhere", "New York", "London", "Tokyo", 
    "Sydney", "Toronto", "Berlin", "Paris", "Mumbai", 
    "San Francisco", "Chicago", "Los Angeles", "Boston", 
    "Seattle", "Austin", "Dubai", "Hong Kong", "Amsterdam"
]

EMAIL_DOMAINS = [
    "company.com", "corp.com", "enterprise.com", "business.com", 
    "organization.com", "firm.com"
]

def generate_employee_id(index: int) -> str:
    """Generate a unique employee ID"""
    return f"EMP{index:04d}"

def generate_email(first_name: str, last_name: str) -> str:
    """Generate a realistic email address"""
    domain = random.choice(EMAIL_DOMAINS)
    # Clean names for email
    first_clean = first_name.lower().replace(" ", "").replace("test", "")[:10]
    last_clean = last_name.lower().replace(" ", "").replace("test", "")[:10]
    
    if not first_clean:
        first_clean = "employee"
    if not last_clean:
        last_clean = "user"
    
    return f"{first_clean}.{last_clean}@{domain}"

def generate_phone() -> str:
    """Generate a realistic phone number"""
    area_codes = ["212", "415", "310", "650", "408", "202", "312", "713"]
    area_code = random.choice(area_codes)
    number = f"{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    return f"+1-{area_code}-{number}"

def generate_sample_employees(count: int = 50) -> list[Employee]:
    """Generate a list of sample employees"""
    employees = []
    
    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        
        # Some employees might not have complete information
        department = random.choice(DEPARTMENTS) if random.random() > 0.1 else None
        position = random.choice(POSITIONS) if random.random() > 0.1 else None
        location = random.choice(LOCATIONS) if random.random() > 0.05 else None
        
        # Most employees are active
        status = StatusEnum.ACTIVE if random.random() > 0.05 else random.choice([StatusEnum.INACTIVE, StatusEnum.TERMINATED])
        
        employee = Employee(
            id=generate_employee_id(i + 1),
            first_name=first_name,
            last_name=last_name,
            email=generate_email(first_name, last_name),
            phone=generate_phone() if random.random() > 0.2 else None,
            department=department,
            position=position,
            location=location,
            status=status
        )
        
        employees.append(employee)
    
    return employees

def main():
    """Main function to populate the database"""
    print("🚀 Generating sample HR database with 1M employees...")
    start_time = time.time()
    
    # Clear existing data
    db.clear_all()
    
    # Generate sample employees in batches for better memory management
    batch_size = 10000
    total_employees = 30000
    
    print(f"📊 Generating {total_employees:,} employees in batches of {batch_size:,}...")
    
    total_added = 0
    for batch_start in range(0, total_employees, batch_size):
        batch_end = min(batch_start + batch_size, total_employees)
        batch_count = batch_end - batch_start
        
        print(f"   Processing batch {batch_start//batch_size + 1}/{(total_employees-1)//batch_size + 1}: employees {batch_start+1:,} to {batch_end:,}")
        
        # Generate batch of employees
        sample_employees = generate_sample_employees(batch_count)
        
        # Update employee IDs to be sequential
        for i, employee in enumerate(sample_employees):
            employee.id = generate_employee_id(batch_start + i + 1)
        
        # Add employees to database
        for employee in sample_employees:
            db.add_employee(employee)
        
        total_added += len(sample_employees)
        
        # Progress update
        progress = (total_added / total_employees) * 100
        print(f"   ✅ Added {len(sample_employees):,} employees. Total: {total_added:,} ({progress:.1f}%)")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Successfully generated {total_added:,} sample employees!")
    print(f"⏱️  Generation completed in {duration:.2f} seconds ({total_added/duration:.0f} employees/sec)")
    
    # Display some statistics
    all_employees = db.get_all_employees()
    active_count = len([emp for emp in all_employees if emp.status == StatusEnum.ACTIVE])
    departments = set(emp.department for emp in all_employees if emp.department)
    locations = set(emp.location for emp in all_employees if emp.location)
    
    print(f"\n📊 Database Statistics:")
    print(f"   - Total employees: {len(all_employees):,}")
    print(f"   - Active employees: {active_count:,}")
    print(f"   - Departments: {len(departments)}")
    print(f"   - Locations: {len(locations)}")
    
    print(f"\n🔍 Sample employees:")
    for i, emp in enumerate(all_employees[:5]):
        print(f"   {i+1}. {emp.first_name} {emp.last_name} - {emp.department or 'No dept'} - {emp.location or 'No location'}")
    
    print(f"\n💾 Database Information:")
    print(f"   - Type: SQLite")
    print(f"   - Location: data/employees.db")
    print(f"   - File size: ~{(total_added * 0.5):.0f} MB (estimated)")
    print(f"   - Persistent: ✅ Data will persist between restarts")
    
    print(f"\n🌐 API is ready! Start the server with:")
    print(f"   uvicorn src.main:app --reload")
    print(f"   Then visit: http://localhost:8000/docs")
    
    print(f"\n💡 Performance Tips:")
    print(f"   - 1M records generated in batches for memory efficiency")
    print(f"   - Use API pagination (limit/offset) for large result sets")
    print(f"   - Consider indexing on frequently searched fields")

if __name__ == "__main__":
    main() 