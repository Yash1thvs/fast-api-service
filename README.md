# Backend (FastAPI)
The backend provides a RESTful API for fetching cost details of clients, tasks, and users. It connects to a PostgreSQL database and provides endpoints for viewing client costs categorized by task, and further by user.

## Features
- List all clients.
- Fetch cost details of clients for a specific month.
- Drill down into costs by task and users.
  
## Requirements
- Python 3.8+
- FastAPI and related libraries
- SQLAlchemy for ORM
- PostgreSQL (or any SQL database)
- Uvicorn for serving the FastAPI app

## Setup Instructions

1. Clone the repository:
```
git clone https://github.com/your-repo/flask-api-services.git
```
2. Set up environment variables:
```
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<dbname>
```
3. Run the FastAPI server:
```
uvicorn main:app --reload
```
This will start the FastAPI server at http://localhost:8000.

## Key API Endpoints
- List Clients (Paginated):
  ```
  GET /clients
  ```
  Fetches a list of clients.

- Get Client Cost Details by Month:
  ```
  GET /clients/{client_id}/cost?month=10
  ```
  Fetches the cost details for the given client and month, categorized by tasks and user.
  
## Database Models
- ClientModel: Stores client information.
- Task: Stores task information associated with clients.
- User: Stores user information.
- Message: Tracks messages and execution of tasks.
- HandlerPricing: Defines pricing for various handlers used in tasks.




