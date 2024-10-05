from fastapi import FastAPI

app = FastAPI()

# Include your routers or routes
from app.api import router as api_router
app.include_router(api_router)