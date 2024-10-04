from fastapi import FastAPI, HTTPException
from app.database import database

app = FastAPI()


# Connect to the database on startup
@app.on_event("startup")
async def startup():
    await database.connect()


# Disconnect from the database on shutdown
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# Health check endpoint to confirm database connection
@app.get("/check-connection")
async def check_connection():
    try:
        query = "SELECT 1"
        await database.execute(query=query)
        return {"status": "Database connection is successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

