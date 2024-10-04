from fastapi import FastAPI, HTTPException, Query
from typing import List
from app.database import database
from app.schemas import ClientResponse, PaginatedClientsResponse

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


# Endpoint to get all clients with pagination
@app.get("/clients", response_model=PaginatedClientsResponse)
async def get_clients(limit: int = 10, offset: int = 0):

    query = """
        SELECT id, title, created_time, modified_time, is_disabled, is_deleted, default_language
        FROM clients
        LIMIT :limit OFFSET :offset
    """
    try:
        clients = await database.fetch_all(query, values={"limit": limit, "offset": offset})

        # Query to get the total count of clients
        count_query = "SELECT COUNT(*) FROM clients"
        total = await database.fetch_one(count_query)

        return {"total": total[0], "clients": clients}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="An error occurred while fetching clients.")

