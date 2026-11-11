# Employee Management API

A beginner-friendly REST API built with FastAPI, SQLAlchemy, and SQLite. Employee
records are saved in `employee.db` and remain available after the server restarts.

## Project files

- `app/__init__.py` marks `app` as a Python package.
- `app/database.py` configures the SQLite connection and provides one database
  session for each request.
- `app/models.py` defines the SQLAlchemy `Employee` table, including the primary
  key, unique email, required fields, and positive-salary database constraint.
- `app/schemas.py` defines Pydantic request and response schemas and validates
  email format, non-blank text, and positive salary.
- `app/crud.py` contains the SQLAlchemy queries for create, read, update, and
  delete operations.
- `app/main.py` creates the database table and defines the FastAPI endpoints.
- `main.py` preserves the previous `uvicorn main:app` launch command.
- `employee.db` is created automatically next to the project files and is
  excluded from Git so employee data is not committed.

## Installation and execution

Requires Python 3.10 or newer. From PowerShell in the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The existing command remains available:

```powershell
python -m uvicorn main:app --reload
```

The API is available at <http://127.0.0.1:8000>. The SQLite database and
`employees` table are created automatically when the application starts.

## API endpoints

| Method | Path | Purpose | Success status |
|---|---|---|---|
| `POST` | `/employees` | Create an employee. Duplicate employee IDs or email addresses return `409 Conflict`. | `201 Created` |
| `GET` | `/employees` | Retrieve all employees, or an empty list if there are none. | `200 OK` |
| `GET` | `/employees/{employee_id}` | Retrieve an employee by ID. Returns `404 Not Found` if missing. | `200 OK` |
| `PUT` | `/employees/{employee_id}` | Replace an employee's details. The body ID must match the URL ID. Returns `404 Not Found` if missing, `400 Bad Request` for an ID mismatch, or `409 Conflict` for a duplicate email. | `200 OK` |
| `DELETE` | `/employees/{employee_id}` | Delete an employee. Returns `404 Not Found` if missing. | `200 OK` |

### Example request body

Use this JSON body for `POST /employees` and `PUT /employees/1`:

```json
{
  "employee_id": 1,
  "name": "Jordan Lee",
  "email": "jordan.lee@example.com",
  "department": "Engineering",
  "salary": 75000.0,
  "designation": "Software Engineer"
}
```

The API requires an integer employee ID, a valid email address, non-blank name,
department, and designation, and a salary greater than zero. Invalid request
data returns `422 Unprocessable Entity`. Unexpected database errors are logged
and return `500 Internal Server Error`.

## Test with Swagger UI

1. Start the server using either command above.
2. Open <http://127.0.0.1:8000/docs>.
3. Expand an endpoint, select **Try it out**, and provide its path parameters or
   JSON request body.
4. Create an employee with `POST /employees`, then try the GET, PUT, and DELETE
   endpoints using the same employee ID.

## How database sessions work

FastAPI calls `get_db` in `app/database.py` for each request. The dependency
opens a SQLAlchemy session and closes it when the request finishes. The CRUD
functions use that session to query or update SQLite; the employee list is no
longer held in Python memory.
