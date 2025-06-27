from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.v1.api import api_router
from app.core.exceptions import APIException
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A comprehensive API for scientific, statistical, and financial calculations.",
    version="2.0.0"
)

# --- Mount Static Files and Templates ---
# This allows serving HTML, CSS, and JS files.
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --- Custom Exception Handler ---
# This catches our custom APIException and returns a formatted JSON response.
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# --- API Router ---
# Include the main API router from app/api/v1/api.py
app.include_router(api_router, prefix=settings.API_V1_STR)


# --- Frontend Route ---
# Serves the main index.html page as the root URL.
@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def read_root(request: Request):
    """
    Serves the web-based calculator frontend.
    """
    return templates.TemplateResponse("index.html", {"request": request})

# To run the app: uvicorn main:app --reload
