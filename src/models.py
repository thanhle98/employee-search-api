from typing import Optional
from enum import Enum

class StatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    TERMINATED = "TERMINATED"

class Employee:
    def __init__(
        self,
        id: str,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        department: Optional[str] = None,
        position: Optional[str] = None,
        location: Optional[str] = None,
        status: StatusEnum = StatusEnum.ACTIVE
    ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.department = department
        self.position = position
        self.location = location
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "department": self.department,
            "position": self.position,
            "location": self.location,
            "status": self.status.value if isinstance(self.status, StatusEnum) else self.status
        }

    def __repr__(self):
        return f"Employee(id='{self.id}', first_name='{self.first_name}', last_name='{self.last_name}')"
