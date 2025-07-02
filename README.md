# Employee Search API

A simple RESTful API for searching employee records built with FastAPI and native Python sqlite3.

## 🚀 Features

- **Employee Search**: Search employees by name, department, position, location, and status
- **Data Validation**: Input validation and error handling with Pydantic
- **Interactive Documentation**: Automatic Swagger/OpenAPI documentation
- **Native Python**: Uses only Python standard library with sqlite3 (no external database dependencies)

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

2. **Generate sample data**
   ```bash
   python generate_sample_data.py
   ```

3. **Run the application**
   ```bash
   uvicorn src.main:app --reload
   ```

4. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🚦 Installation

### Prerequisites
- Python >= 3.9
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

4. **Generate sample data**
   ```bash
   python generate_sample_data.py
   ```

5. **Run the application**
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
| GET | `/employees/search` | Search employees with query parameters |
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

- **first_name**: Filter by first name (partial match)
- **last_name**: Filter by last name (partial match)  
- **department**: Filter by department (partial match)
- **position**: Filter by position (partial match)
- **location**: Filter by location (partial match)
- **status**: Filter by exact status
- **limit**: Results per page (1-200, default: 50)
- **offset**: Results to skip (default: 0)

### Example Requests

#### GET Search
```bash
GET /api/v1/employees/search?department=Engineering&position=Developer&limit=10
```


## 🧪 Testing

```bash
# Run all tests
pytest
```

## 🔗 Related Links

- [OmniHR Backend Assignment 2](https://omnihr.notion.site/Backend-Assignment-2-cdb352624622474ea7103bf212b13b25)
- API Documentation: `http://localhost:8000/docs` (when running)
