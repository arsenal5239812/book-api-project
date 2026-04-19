from fastapi import FastAPI

from app.database import Base, engine
from app.routers.analytics import router as analytics_router
from app.routers.auth import router as auth_router
from app.routers.books import router as books_router
from app.routers.reviews import router as reviews_router
from app.routers.users import router as users_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Metadata and Recommendation API",
    description="A production-style coursework API with CRUD, authentication, analytics, and SQL persistence.",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(users_router)
app.include_router(reviews_router)
app.include_router(analytics_router)

@app.get("/")
def healthcheck():
    return {"message": "Book Metadata and Recommendation API is running"}
