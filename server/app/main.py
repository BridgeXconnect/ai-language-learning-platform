from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from app.core.config import settings
from app.core.database import engine, Base
from app.routes import auth_routes, course_routes, sales_routes, ai_routes, agent_routes, sop_routes, health_routes

# Import all models to ensure they're registered with SQLAlchemy
from app.models import user, sales
from app.domains.auth.models import User, Role, Permission
from app.domains.sales.models import CourseRequest

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for Dynamic English Course Creator"
)

# Add CORS middleware with enhanced debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600  # Cache preflight for 1 hour
)

# Add startup event to log CORS configuration
@app.on_event("startup")
async def startup_event():
    print(f"🌐 CORS Origins configured: {settings.cors_origins_list}")
    print(f"🔗 API Base URL: {settings.API_BASE_URL if hasattr(settings, 'API_BASE_URL') else 'Not configured'}")
    print("✅ CORS middleware configured for all origins, methods, and headers")
    print("🚀 Server starting up - health check available at /health")

# Include routers
app.include_router(health_routes.router)  # Add health check first
app.include_router(auth_routes.router)
app.include_router(course_routes.router)
app.include_router(sales_routes.router)
app.include_router(ai_routes.router)
app.include_router(agent_routes.router)
app.include_router(sop_routes.router)

# Remove duplicate health check (using dedicated health_routes module)

# Add OPTIONS handler for all routes to fix CORS
@app.options("/{rest_of_path:path}")
async def preflight_handler(request, rest_of_path: str):
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    return response

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {
        "detail": str(exc),
        "status_code": 500
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 