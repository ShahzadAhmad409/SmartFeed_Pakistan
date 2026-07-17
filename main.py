from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from app.routers import auth_router, api_router, web_router
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartFeed Pakistan")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(web_router.router)
app.include_router(auth_router.router, prefix="/auth")
app.include_router(api_router.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
