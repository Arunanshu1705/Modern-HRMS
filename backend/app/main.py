from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.database import init_db
from app.routers import auth, employees, attendance, leave, payroll, skills, company, chatbot, organization, reports

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="PeopleHub HRMS - A comprehensive Human Resource Management System",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization warning: {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to PeopleHub HRMS API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "PeopleHub HRMS API"}


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(organization.router, prefix="/api/organization", tags=["Organization"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(leave.router, prefix="/api/leave", tags=["Leave"])
app.include_router(payroll.router, prefix="/api/payroll", tags=["Payroll"])
app.include_router(skills.router, prefix="/api/skills", tags=["Skills & CV"])
app.include_router(company.router, prefix="/api/company", tags=["Company"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["AI Chatbot"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports & Analytics"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)