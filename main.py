from fastapi import FastAPI
from app.routers import auth, users, projects
from app.database import engine
from app.models.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)

@app.get("/")
async def root():
    return {"message": "Secret Scanner API"}