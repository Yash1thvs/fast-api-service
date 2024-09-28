from typing import Union

import uvicorn
from fastapi import FastAPI
from databases import Database
import sqlalchemy

# Database connection URL (you'll need to replace with your credentials)
DATABASE_URL = "postgresql://test_user:test_user@34.121.45.231:5432/test"

app = FastAPI()

# Initialize the database connection
database = Database(DATABASE_URL)

# SQLAlchemy metadata for schema reflection
metadata = sqlalchemy.MetaData()


# Define a route to check if the database connection is successful
@app.on_event("startup")
async def startup():
    # Connect to the database when the app starts
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    # Disconnect from the database when the app shuts down
    await database.disconnect()


@app.get("/check_db_connection")
async def check_db_connection():
    # Check the connection by running a simple query
    query = "SELECT 1"
    result = await database.fetch_one(query)

    if result:
        return {"status": "Database connection is successful!"}
    else:
        return {"status": "Database connection failed!"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)

