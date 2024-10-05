from fastapi import FastAPI, HTTPException
from typing import List, Optional
from app.database import database
from app.schemas import PaginatedClientsResponse, ClientCostResponse, ClientTotalCostResponse

from datetime import datetime, timedelta
from uuid import UUID

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


# 1. Viewing a list of clients
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


# 2. Select a client to see the cost incurred this month (by default). With an option to select any of the previous
# 12 months.
@app.get("/clients/{client_id}/cost", response_model=ClientTotalCostResponse)
async def get_client_cost(client_id: UUID, year: Optional[int] = None, month: Optional[int] = None):
    try:
        today = datetime.today()

        # Default to current month and year if not provided
        if not year:
            year = today.year
        if not month:
            month = today.month

        # Validate the input: The user can select only up to the previous 12 months
        if year < today.year - 1 or (year == today.year - 1 and month < today.month):
            raise HTTPException(
                status_code=400,
                detail="You can only select data from the current month or the previous 12 months."
            )

        # Query: Retrieve monthly costs and overall total for the client
        query = """
        SELECT 
            c.id::text AS client_id,  -- Cast UUID to text
            c.title AS client_title,
            COALESCE(SUM(
                CASE 
                    WHEN t.form_handler = 'handler_a' THEN 10
                    WHEN t.form_handler = 'handler_b' THEN 20
                    ELSE 5
                END
            ), 0) AS total_cost,
            EXTRACT(YEAR FROM m.created_time) AS year,
            EXTRACT(MONTH FROM m.created_time) AS month
        FROM 
            clients c
        JOIN 
            client_models cm ON cm.client_id = c.id
        JOIN 
            tasks t ON t.client_models_id = cm.id
        JOIN 
            chats ch ON ch.task_id = t.id
        JOIN 
            messages m ON m.chat_id = ch.id
        WHERE 
            m.is_deleted = false
            AND ch.is_deleted = false
            AND c.id = :client_id
            AND EXTRACT(YEAR FROM m.created_time) = :year
            AND EXTRACT(MONTH FROM m.created_time) = :month
        GROUP BY 
            c.id, c.title, year, month
        ORDER BY 
            c.title;
        """

        # Prepare the query values
        values = {"client_id": str(client_id), "year": year, "month": month}

        # Execute the query for the monthly breakdown
        monthly_costs = await database.fetch_all(query=query, values=values)

        # Handle case where no data is found
        if not monthly_costs:
            raise HTTPException(
                status_code=404,
                detail=f"No cost data found for client with ID {client_id} in year {year} and month {month}."
            )

        # Calculate the total cost across all months
        overall_total_cost = sum(item['total_cost'] for item in monthly_costs)

        # Prepare response structure
        response = {
            "client_id": monthly_costs[0]["client_id"],  # Taking the first one since it's grouped by client_id
            "client_title": monthly_costs[0]["client_title"],
            "total_cost": overall_total_cost,  # Total cost for the period
            "monthly_breakdown": monthly_costs  # List of costs per month
        }

        return response

    except Exception as e:
        # Catch any unexpected errors and provide a detailed message
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")