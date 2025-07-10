# Employee Search API

A simple RESTful API for searching employee records built with FastAPI and native Python sqlite3.

## 🚀 Features

- **Employee Search**: Search employees by name, department, position, location, and status with advanced filtering
- **Dynamic Field Selection**: Choose specific fields to return in API responses for optimized performance and reduced bandwidth
- **Pagination**: Efficient pagination with configurable limit and offset parameters
- **Interactive Documentation**: Automatic Swagger/OpenAPI documentation
- **Security**: SQL Injection Prevention and Rate Limiting with field validation
- **Testing**: Comprehensive pytest test suite

## 🛠 Tech Stack

- **Runtime**: Python 3.9+
- **Framework**: FastAPI
- **Database**: SQLite3 (native Python)
- **Testing**: pytest
- **Documentation**: Swagger/OpenAPI

## 📁 Project Structure

```
employee-search-api/
├── src/
│   ├── api/            # API routes
│   ├── middleware/     # Middleware: Rate Limiting 
│   ├── models.py       # Data models
│   ├── database.py     # Database operations (native sqlite3)
│   └── main.py         # FastAPI application
├── tests/              # Test files
├── data/               # Database files
├── requirements.txt    
├── docker-compose.yml  
├── Dockerfile          
└── generate_sample_data.py  # Sample data generator
```

## ⚡ Quick Start

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd employee-search-api
   pip install -r requirements.txt
   ```

2. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

3. **Generate sample data**
   ```bash
   python generate_sample_data.py
   ```

4. **Run the application**
   ```bash
   uvicorn src.main:app --reload
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🚦 Installation

### Prerequisites
- Python 3.9
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd employee-search-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Generate sample data**
   ```bash
   python generate_sample_data.py
   ```

6. **Run the application**
   ```bash
   uvicorn src.main:app --reload
   ```

### Using Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/employees/search` | Search employees with filtering, pagination, and field selection |
| GET | `/health` | Health check |

### Employee Model

```json
{
  "id": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "department": "string",
  "position": "string",
  "location": "string",
  "status": "ACTIVE|INACTIVE|TERMINATED"
}
```

### Search Parameters

#### Filter Parameters
- **first_name**: Filter by first name (partial match)
- **last_name**: Filter by last name (partial match)  
- **department**: Filter by department (partial match)
- **position**: Filter by position (partial match)
- **location**: Filter by location (partial match)
- **status**: Filter by exact status (`ACTIVE`, `INACTIVE`, `TERMINATED`)

#### Pagination Parameters
- **limit**: Results per page (1-200, default: 50)
- **offset**: Results to skip (default: 0)

#### Field Selection Parameter
- **select**: Comma-separated list of fields to return in the response
  - **Available fields**: `id`, `first_name`, `last_name`, `email`, `phone`, `department`, `position`, `location`, `status`
  - **Default**: All fields are returned if not specified
  - **Example**: `select=id,first_name,last_name,email` - returns only ID, name, and email fields
  - **Benefits**: Reduces response size, improves performance, and minimizes bandwidth usage
  - **Security**: Only whitelisted fields are allowed to prevent SQL injection

### Example Requests

#### Basic Search
```bash
# Search by department and position
GET /api/v1/employees/search?department=Engineering&position=Developer&limit=10

# Search by name with pagination
GET /api/v1/employees/search?first_name=John&limit=5&offset=10
```

#### Field Selection Examples
```bash
# Get only basic contact information
GET /api/v1/employees/search?select=id,first_name,last_name,email

# Get only names and department for organizational chart
GET /api/v1/employees/search?select=id,first_name,last_name,department

# Get minimal employee list for dropdown
GET /api/v1/employees/search?select=id,first_name,last_name&status=ACTIVE&limit=100

# Combine filtering with field selection
GET /api/v1/employees/search?department=Sales&select=first_name,last_name,position,email
```

#### Advanced Search Examples
```bash
# Search active developers with contact info only
GET /api/v1/employees/search?position=Developer&status=ACTIVE&select=id,first_name,last_name,email,phone

# Get department statistics (names and departments only)
GET /api/v1/employees/search?select=first_name,last_name,department&limit=200
```

### Response Examples

#### Full Employee Response (default - no select parameter)
```json
{
  "employees": [
    {
      "id": "emp_001",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@company.com",
      "phone": "+1-555-123-4567",
      "department": "Engineering",
      "position": "Senior Developer",
      "location": "New York",
      "status": "ACTIVE"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

#### Selected Fields Response (with select=id,first_name,last_name,department)
```json
{
  "employees": [
    {
      "id": "emp_001",
      "first_name": "John",
      "last_name": "Doe",
      "department": "Engineering"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```


## 🧪 Testing

```bash
# Run test one by one to avoid rate limit
pytest tests/test_search.py -v
pytest tests/test_rate_limit.py -v
```

## 🔗 Related Links

- [OmniHR Backend Assignment 2](https://omnihr.notion.site/Backend-Assignment-2-cdb352624622474ea7103bf212b13b25)
- API Documentation: `http://localhost:8000/docs` (when running)
