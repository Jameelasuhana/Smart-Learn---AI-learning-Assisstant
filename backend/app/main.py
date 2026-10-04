import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, ai, youtube, tests, attempts, progress

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("smart_learn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    logger.info("Initializing Smart Learn backend services...")
    await connect_to_mongo()
    yield
    # Shutdown: Close MongoDB connection
    logger.info("Shutting down Smart Learn backend...")
    await close_mongo_connection()

app = FastAPI(
    title="SMART LEARN – AI-Powered Learning Assistant",
    description="Full-stack AI personalized learning and assessment API powered by Gemini & MongoDB Atlas.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(youtube.router)
app.include_router(tests.router)
app.include_router(attempts.router)
app.include_router(progress.router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "app_name": "Smart Learn",
        "message": "Welcome to Smart Learn – AI-Powered Learning Assistant API",
        "docs_url": "/docs"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
