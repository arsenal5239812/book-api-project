from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import HTMLResponse

from app.config import settings
from app.routers.analytics import router as analytics_router
from app.routers.auth import router as auth_router
from app.routers.books import router as books_router
from app.routers.reviews import router as reviews_router
from app.routers.users import router as users_router

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    openapi_url=settings.openapi_url,
    docs_url=settings.docs_url,
    redoc_url=None,
)

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(users_router)
app.include_router(reviews_router)
app.include_router(analytics_router)

@app.get("/")
def healthcheck():
    return {"message": settings.healthcheck_message}


@app.get(settings.redoc_url, include_in_schema=False)
def custom_redoc_html() -> HTMLResponse:
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url=settings.redoc_js_url,
    )
