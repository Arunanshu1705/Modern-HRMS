# PeopleHub HRMS

A comprehensive Human Resource Management System built with FastAPI, Streamlit, PostgreSQL, and AI-powered chatbot assistance.

## Features

- **Authentication & Authorization**: JWT-based secure authentication with role-based access control (Employee/Admin)
- **Employee Management**: Complete employee directory with profile management
- **Attendance Management**: Check-in/check-out system with attendance tracking and analytics
- **Leave Management**: Leave application, approval workflow, and leave balance tracking
- **Payroll Management**: Salary details, payroll processing, and PDF payslip generation
- **CV/Skills Database**: Employee skills, tools, projects, work experience, and certifications
- **Employee Matching**: AI-powered employee matching for project requirements
- **Announcements**: Company announcements and updates
- **Holiday Management**: Holiday calendar management
- **Reports & Analytics**: Comprehensive reporting with visualizations
- **AI Chatbot**: Intelligent HRMS assistant with natural language processing

## Technology Stack

### Backend

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy 2.0**: Python SQL toolkit and ORM
- **Alembic**: Database migration tool
- **PostgreSQL**: Relational database
- **Pydantic**: Data validation using Python type annotations
- **JWT & OAuth2**: Authentication and authorization
- **ReportLab**: PDF generation for payslips
- **OpenAI API**: AI chatbot functionality

### Frontend

- **Streamlit**: Python framework for creating web applications
- **Plotly**: Interactive charts and graphs
- **Pandas**: Data manipulation and analysis
- **Requests**: HTTP library for API calls

### Deployment

- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## Project Structure

```
PeopleHub/
│
├── backend/
│ ├── app/
│ │ ├── main.py                 # FastAPI application entry point
│ │ ├── core/                   # Core functionality
│ │ │ ├── config.py            # Configuration settings
│ │ │ ├── security.py          # Security utilities (JWT, password hashing)
│ │ │ └── dependencies.py      # FastAPI dependencies
│ │ ├── database/              # Database configuration
│ │ │ ├── database.py          # Database session management
│ │ │ └── base.py              # Base models and mixins
│ │ ├── models/                 # SQLAlchemy models
│ │ ├── schemas/                # Pydantic schemas
│ │ ├── routers/                # API route handlers
│ │ ├── services/               # Business logic services
│ │ └── ai/                     # AI chatbot components
│ │ ├── service.py             # AI chatbot service
│ │ ├── prompts.py             # AI prompts
│ │ ├── intents.py             # Intent definitions
│ │ ├── tools.py               # AI tools for HRMS data access
│ │ └── permissions.py         # Role-based permissions
│ ├── alembic/                 # Database migrations
│ ├── requirements.txt          # Python dependencies
│ ├── .env.example             # Environment variables template
│ ├── seed_data.py             # Database seeding script
│ └── Dockerfile               # Docker configuration
│
├── frontend/
│ ├── app.py                   # Streamlit application entry point
│ ├── pages/                   # Streamlit pages
│ ├── services/                # API client services
│ ├── utils/                   # Utility functions
│ ├── assets/                  # Static assets
│ ├── requirements.txt          # Python dependencies
│ └── Dockerfile               # Docker configuration
│
├── tests/                     # Test files
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Root Dockerfile
├── README.md                  # This file
└── .gitignore                 # Git ignore rules
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker (optional, for containerized deployment)

### Local Development Setup

#### 1. Clone the repository

```bash
git clone <repository-url>
cd PeopleHub
```

#### 2. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Edit .env file with your configuration
# DATABASE_URL=postgresql://postgres:password@localhost:5432/peoplehub
# SECRET_KEY=your-secret-key-here
# OPENAI_API_KEY=your-openai-api-key-here
```

#### 3. Database Setup

```powershell
# Start PostgreSQL service (if not already running)
# Make sure PostgreSQL is installed and running

# Initialize database
python -c "from app.database.database import init_db; init_db()"

# Run database migrations
alembic upgrade head

# Seed database with sample data
python seed_data.py
```

#### 4. Frontend Setup

```powershell
# Navigate to frontend directory
cd ..\frontend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo API_BASE_URL=http://localhost:8000 > .env
```

#### 5. Running the Application

```powershell
# Terminal 1: Start FastAPI backend
cd backend
.\venv\Scripts\Activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Streamlit frontend
cd frontend
.\venv\Scripts\Activate
streamlit run app.py --server.port 8501
```

Access the application at:

- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Docker Deployment

#### Using Docker Compose

```powershell
# Build and start all services
docker-compose up --build

# The application will be available at:
# Frontend: http://localhost:8501
# Backend: http://localhost:8000
# PostgreSQL: localhost:5432
```

#### Individual Docker Commands

```powershell
# Build backend
docker build -t peoplehub-backend ./backend

# Build frontend
docker build -t peoplehub-frontend ./frontend

# Run PostgreSQL
docker run -d --name peoplehub-postgres -e POSTGRES_DB=peoplehub -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15

# Run backend
docker run -d --name peoplehub-backend -p 8000:8000 --link peoplehub-postgres:postgres -e DATABASE_URL=postgresql://postgres:password@postgres:5432/peoplehub peoplehub-backend

# Run frontend
docker run -d --name peoplehub-frontend -p 8501:8501 -e API_BASE_URL=http://localhost:8000 peoplehub-frontend
```

## Sample Credentials

After running the seed data script, you can use these credentials to log in:

### Admin Account

- **User ID**: `admin`
- **Password**: `admin123`

### Employee Accounts

- **User ID**: `john.doe`
- **Password**: `password123`

- **User ID**: `jane.smith`
- **Password**: `password123`

- **User ID**: `bob.johnson`
- **Password**: `password123`

- **User ID**: `alice.williams`
- **Password**: `password123`

- **User ID**: `charlie.brown`
- **Password**: `password123`

## API Documentation

Once the backend is running, access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Migrations

### Create a new migration

```powershell
cd backend
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations

```powershell
cd backend
alembic upgrade head
```

### Rollback migrations

```powershell
cd backend
alembic downgrade -1
```

## Testing

### Run all tests

```powershell
cd backend
pytest
```

### Run specific test file

```powershell
cd backend
pytest tests/test_auth.py
```

### Run with coverage

```powershell
cd backend
pytest --cov=app --cov-report=html
```

## AI Chatbot

The AI chatbot uses OpenAI's GPT model to provide intelligent assistance. To enable the chatbot:

1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Add the API key to your `.env` file:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```
3. Restart the backend service

The chatbot can:

- Navigate users to appropriate HRMS sections
- Retrieve user-specific information (attendance, leave balance, salary, etc.)
- Assist with HRMS operations (with confirmation)
- Answer HRMS-related questions
- Provide role-appropriate assistance

## Features by Role

### Employee Features

- View personal dashboard
- Mark attendance (check-in/check-out)
- Apply for leave
- View leave balance and history
- View salary details and payslips
- Update skills, tools, projects, work experience, certifications
- View announcements and holidays
- Access AI chatbot for assistance

### Admin Features

- All employee features plus:
- Manage employees (add, edit, deactivate)
- View attendance overview and analytics
- Approve/reject leave requests
- Manage payroll and generate payslips
- Manage skills, tools, and projects
- Employee matching for projects
- Create and manage announcements
- Manage holidays
- Generate comprehensive reports
- Access admin-specific AI chatbot features

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- API endpoint authorization
- Input validation with Pydantic
- Secure environment variable management
- No hard-coded secrets
- HTTPS-ready architecture

## Performance Considerations

- Database query optimization with indexes
- Efficient API response times
- Pagination for large datasets
- Caching where appropriate
- Optimized database connections
- Efficient chatbot response handling

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Check DATABASE_URL in .env file
- Verify database credentials
- Check PostgreSQL logs

### Authentication Issues

- Verify JWT token configuration
- Check SECRET_KEY in .env file
- Ensure password hashing is working correctly
- Verify user roles are properly set

### AI Chatbot Issues

- Verify OPENAI_API_KEY is set correctly
- Check OpenAI API quota
- Review chatbot service logs
- Test with simple messages first

### Docker Issues

- Ensure Docker is running
- Check Docker logs: `docker-compose logs`
- Verify port availability
- Check network connectivity between containers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the API documentation at /docs endpoint

## Roadmap

Future enhancements:

- Mobile application
- Advanced analytics dashboard
- Integration with external HR systems
- Enhanced AI capabilities
- Performance optimization
- Additional reporting features
- Multi-language support
