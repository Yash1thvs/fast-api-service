from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from app.database import database
from app.schemas import PaginatedClientsResponse, ClientCostResponse, ClientTotalCostResponseCategory, ClientCostResponseUser

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

@app.get("/clients/{client_id}/monthly-cost", response_model=ClientCostResponse)
async def get_client_monthly_cost(client_id: UUID, year: Optional[int] = None, month: Optional[int] = None):
    try:
        # Get the current year and month if not provided
        today = datetime.today()
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

        # SQL Query: Fetch the total cost for the given client for the specified year and month
        query = """
        SELECT 
            COALESCE(SUM(
                CASE 
                    WHEN t.form_handler = 'handler_a' THEN 10
                    WHEN t.form_handler = 'handler_b' THEN 20
                    ELSE 5
                END
            ), 0) AS total_cost
        FROM 
            messages m
        JOIN 
            chats ch ON m.chat_id = ch.id
        JOIN 
            tasks t ON ch.task_id = t.id
        JOIN 
            client_models cm ON t.client_models_id = cm.id
        JOIN 
            clients c ON cm.client_id = c.id
        WHERE 
            m.is_deleted = false
            AND ch.is_deleted = false
            AND c.id = :client_id
            AND EXTRACT(YEAR FROM m.created_time) = :year
            AND EXTRACT(MONTH FROM m.created_time) = :month;
        """

        values = {"client_id": str(client_id), "year": year, "month": month}
        result = await database.fetch_one(query=query, values=values)

        # Handle case where no data is found
        if result is None or result["total_cost"] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No cost data found for client with ID {client_id} in year {year} and month {month}."
            )

        # Build and return the response
        response = {
            "client_id": str(client_id),
            "total_cost": result["total_cost"],
            "year": year,
            "month": month
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# 3. Show the total cost categorised by the category (handler_pricing.title) and within the category by task name (
# tasks.title). This will show the number of messages for each task and the total cost for that task.
@app.get("/clients/{client_id}/cost", response_model=ClientTotalCostResponseCategory)
async def get_client_cost(client_id: UUID, year: Optional[int] = None, month: Optional[int] = None):
    try:
        # Default to current month and year if not provided
        today = datetime.today()
        if not year:
            year = today.year
        if not month:
            month = today.month

        # Validate input to ensure the selected period is within the last 12 months
        if year < today.year - 1 or (year == today.year - 1 and month < today.month):
            raise HTTPException(
                status_code=400,
                detail="You can only select data from the current month or the previous 12 months."
            )

        # SQL Query: Fetch the total cost and number of messages categorized by handler_pricing.title and tasks.title
        query = """
        SELECT 
            hp.title AS handler_category,
            t.title AS task_title,
            COUNT(m.id) AS message_count,
            COALESCE(SUM(hp.execution_price), 0) AS total_cost
        FROM 
            messages m
        JOIN 
            chats ch ON m.chat_id = ch.id
        JOIN 
            tasks t ON ch.task_id = t.id
        JOIN 
            client_models cm ON t.client_models_id = cm.id
        JOIN 
            clients c ON cm.client_id = c.id
        LEFT JOIN 
            handler_pricing hp ON t.form_handler = hp.handler_name
        WHERE 
            m.is_deleted = false
            AND ch.is_deleted = false
            AND c.id = :client_id
            AND EXTRACT(YEAR FROM m.created_time) = :year
            AND EXTRACT(MONTH FROM m.created_time) = :month
        GROUP BY 
            hp.title, t.title
        ORDER BY 
            hp.title, t.title;
        """

        values = {"client_id": str(client_id), "year": year, "month": month}
        result = await database.fetch_all(query=query, values=values)

        # Handle case where no data is found
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No cost data found for client with ID {client_id} in year {year} and month {month}."
            )

        # Build response
        categories_dict = {}
        for row in result:
            handler_category = row['handler_category']
            task_title = row['task_title']
            message_count = row['message_count']
            total_cost = row['total_cost']

            if handler_category not in categories_dict:
                categories_dict[handler_category] = {
                    "handler_category": handler_category,
                    "tasks": []
                }

            categories_dict[handler_category]["tasks"].append({
                "task_title": task_title,
                "message_count": message_count,
                "total_cost": total_cost
            })

        # Convert to the final structure
        categories = list(categories_dict.values())
        total_cost = sum([task["total_cost"] for category in categories for task in category["tasks"]])

        response = {
            "client_id": str(client_id),
            "total_cost": total_cost,
            "categories": categories
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/clients/{client_id}/category-costs", response_model=ClientCostResponseUser)
async def get_category_costs(
    client_id: UUID,
    year: Optional[int] = None,
    month: Optional[int] = None,
    user_email: Optional[str] = None
):
    try:
        # Get current year and month if not provided
        today = datetime.today()
        if not year:
            year = today.year
        if not month:
            month = today.month

        # SQL query: Retrieve the total cost and message count grouped by category and task
        query = """
        SELECT 
            hp.title AS category_title,
            t.title AS task_title,
            COUNT(m.id) AS message_count,
            SUM(
                CASE 
                    WHEN t.form_handler = 'handler_a' THEN 10
                    WHEN t.form_handler = 'handler_b' THEN 20
                    ELSE 5
                END
            ) AS total_cost
        FROM 
            messages m
        JOIN 
            chats ch ON m.chat_id = ch.id
        JOIN 
            tasks t ON ch.task_id = t.id
        JOIN 
            handler_pricing hp ON t.form_handler = hp.handler_name
        JOIN 
            client_models cm ON t.client_models_id = cm.id
        JOIN 
            clients c ON cm.client_id = c.id
        -- Change here: Join users based on `ch.user_id` instead of `m.user_id`
        LEFT JOIN 
            users u ON ch.user_id = u.id
        WHERE 
            m.is_deleted = false
            AND ch.is_deleted = false
            AND c.id = :client_id
            AND EXTRACT(YEAR FROM m.created_time) = :year
            AND EXTRACT(MONTH FROM m.created_time) = :month
        """

        # Add user email filter if provided
        if user_email:
            query += " AND u.email = :user_email"

        # Group by category and task
        query += """
        GROUP BY 
            hp.title, t.title
        ORDER BY 
            hp.title, t.title;
        """

        # Prepare values for the query
        values = {"client_id": str(client_id), "year": year, "month": month}
        if user_email:
            values["user_email"] = user_email

        # Execute the query
        results = await database.fetch_all(query=query, values=values)

        # Handle the case where no data is found
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No cost data found for client with ID {client_id} in year {year} and month {month}."
            )

        # Process the results into the desired response structure
        categories = {}
        total_cost = 0

        for row in results:
            category_title = row["category_title"]
            task_title = row["task_title"]
            message_count = row["message_count"]
            task_cost = row["total_cost"]

            total_cost += task_cost

            # Group tasks under their categories
            if category_title not in categories:
                categories[category_title] = {"category_title": category_title, "tasks": []}

            categories[category_title]["tasks"].append({
                "task_title": task_title,
                "message_count": message_count,
                "total_cost": task_cost
            })

        # Prepare final response
        response = {
            "client_id": str(client_id),
            "total_cost": total_cost,
            "categories": list(categories.values())
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

