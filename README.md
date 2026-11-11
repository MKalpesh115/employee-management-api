# Employee Management API

A beginner-friendly REST API built with FastAPI. It supports creating, listing,
retrieving, updating, and deleting employee records. Records are stored in a
Python list, so they are cleared whenever the application restarts.

## Requirements

- Python 3.10 or newer
- pip

## Installation and execution

Open a terminal in the project directory and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

The API will be available at <http://127.0.0.1:8000>.

## API endpoints

| Method | Path | Purpose | Success status |
|---|---|---|---|
| `POST` | `/employees` | Add an employee. Returns `409 Conflict` if the ID already exists. | `201 Created` |
| `GET` | `/employees` | Retrieve all employees. Returns an empty list if there are none. | `200 OK` |
| `GET` | `/employees/{employee_id}` | Retrieve one employee. Returns `404 Not Found` if missing. | `200 OK` |
| `PUT` | `/employees/{employee_id}` | Replace all fields of an existing employee. Returns `404 Not Found` if missing and `400 Bad Request` if the body ID differs from the URL ID. | `200 OK` |
| `DELETE` | `/employees/{employee_id}` | Delete an employee and return a confirmation message. Returns `404 Not Found` if missing. | `200 OK` |

### Employee JSON body

Use the following body for both `POST` and `PUT`:

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

The employee ID must be unique when creating a record. Names, departments,
and designations cannot be blank; emails must be valid; and salary must be
greater than zero. Invalid input returns FastAPI's validation response with
status `422 Unprocessable Entity`.

## Try it in Swagger UI

1. Start the server using the command above.
2. Open <http://127.0.0.1:8000/docs> in a browser.
3. Select an endpoint and click **Try it out**.
4. For `POST /employees`, paste the example JSON body and click **Execute**.
5. Try `GET /employees` or `GET /employees/1` to view the record.
6. To update it, use `PUT /employees/1` with a complete JSON body whose
   `employee_id` is also `1`. Use `DELETE /employees/1` to remove it.

## How the code is organized

- `Employee` is a Pydantic model. It validates incoming employee fields,
  including email format, positive salary, and non-blank text.
- `employees` is the in-memory Python list that stores records.
- `find_employee_index` centralizes employee lookup and raises a `404` error
  when the requested ID does not exist.
- Each FastAPI endpoint handles one CRUD operation and declares its success
  response model or status code.
