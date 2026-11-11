# Employee Management API

A REST API using FastAPI, SQLAlchemy, and SQLite. It provides user registration
and login, Argon2 password hashing, JWT bearer authentication, and authenticated
employee CRUD operations. Employee and user records persist in `employee.db`.

## Project files

- `app/__init__.py` marks `app` as a Python package.
- `app/database.py` configures SQLite and supplies a SQLAlchemy session per
  request. It reads `DATABASE_URL` from the environment and creates the parent
  folder for file-based SQLite databases before connecting. Tests can select a
  separate database through `DATABASE_URL`.
- `app/models.py` defines the employee and user database tables.
- `app/schemas.py` defines Pydantic request and response schemas.
- `app/auth.py` hashes passwords, registers and authenticates users, issues and
  verifies JWTs, and defines the `/auth` routes.
- `app/crud.py` implements employee database operations and database conflict
  handling.
- `app/main.py` initializes database tables, configures error handling, and
  defines the protected employee endpoints.
- `tests/conftest.py` configures a test-only signing key and isolated in-memory
  SQLite database for the test suite.
- `tests/test_auth.py` and `tests/test_employees.py` test authentication and
  employee endpoints.
- `main.py` preserves the previous `uvicorn main:app` launch command.
- `.env.example` documents the required secret variable without containing a
  real secret.
- `.gitignore` excludes local databases, test artifacts, and environment files.

## Installation and execution

Requires Python 3.10 or newer. In PowerShell from the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
Set-Content -Path .env -Value ("JWT_SECRET_KEY=" + (python -c "import secrets; print(secrets.token_urlsafe(32))"))
python -m uvicorn app.main:app --env-file .env --reload
```

Keep the generated signing key private. The application requires
`JWT_SECRET_KEY` to be set to at least 32 characters before it starts. The local
Uvicorn command loads it from `.env`; do not commit or share that file.

The existing launch command also works:

```powershell
python -m uvicorn main:app --env-file .env --reload
```

The API is available at <http://127.0.0.1:8000>. The database tables are created
automatically when the application starts.

## Run the application with Docker

The Docker setup adds three files:

- `Dockerfile` builds the API image on the official lightweight `python:3.12-slim`
  image, installs `requirements.txt`, copies the application, and starts Uvicorn
  listening on `0.0.0.0:8000`. The app runs as a non-root user.
- `.dockerignore` prevents Git files, virtual environments, caches, local
  databases, tests, and `.env` credentials from being sent to the image build.
- `compose.yaml` maps host port `8000` to container port `8000`, provides the
  JWT secret from the environment, and mounts a named persistent volume at
  `/data` for SQLite.

Docker Compose sets `DATABASE_URL` to `sqlite:////data/employee.db`. The
application creates `/data` if needed before SQLAlchemy connects. Local
execution continues to use the existing project-level `employee.db` default.

### Prepare the JWT secret

In PowerShell, create a local `.env` file containing a randomly generated secret:

```powershell
Copy-Item .env.example .env
Set-Content -Path .env -Value ("JWT_SECRET_KEY=" + (python -c "import secrets; print(secrets.token_urlsafe(32))"))
```

`.env` is ignored by Git and excluded from the Docker build. Do not share or
commit it. Compose reads it for variable substitution and passes only the
`JWT_SECRET_KEY` setting into the container.

### Build and run with Docker Compose

```powershell
docker compose up --build -d
```

This builds the image if needed and starts the application in the background.
Open <http://localhost:8000/docs> for Swagger UI.

### Build and run with Docker commands

Build the image:

```powershell
docker build -t employee-management-api .
```

Run the container with the persistent database volume:

```powershell
docker run --name employee-api -p 8000:8000 --env-file .env -e DATABASE_URL=sqlite:////data/employee.db -v employee_data:/data employee-management-api
```

The same named volume, `employee_data`, keeps SQLite data when the container is
removed and recreated.

### Useful Docker commands

View running containers:

```powershell
docker ps
```

Follow logs from the standalone container:

```powershell
docker logs -f employee-api
```

Stop and remove the standalone container (the named data volume is retained):

```powershell
docker stop employee-api
docker rm employee-api
```

View Compose logs:

```powershell
docker compose logs -f api
```

Stop and remove the Compose container and network (the named data volume is
retained):

```powershell
docker compose down
```

To delete the saved database too, use `docker compose down --volumes`; this
permanently removes the Compose-managed database volume.

### Verify with Swagger UI

1. Start Docker Compose and open <http://localhost:8000/docs>.
2. Register a user with `POST /auth/register`.
3. Log in with `POST /auth/login` and copy the returned `access_token`.
4. Click **Authorize** in Swagger UI and provide the token as a bearer token.
5. Try the employee CRUD endpoints. They should work with the token and return
   `401 Unauthorized` without it.

## Authentication

| Method | Path | Purpose | Success status |
|---|---|---|---|
| `POST` | `/auth/register` | Register a user; duplicate usernames or emails return `409 Conflict`. The response never includes the password hash. | `201 Created` |
| `POST` | `/auth/login` | Verify email and password, then return a short-lived access token. Incorrect credentials return `401 Unauthorized`. | `200 OK` |

Example registration body:

```json
{
  "username": "alex",
  "email": "alex@example.com",
  "password": "a-secure-password"
}
```

Passwords must be at least eight characters. They are stored as Argon2 hashes,
never as plain text.

Example login body:

```json
{
  "email": "alex@example.com",
  "password": "a-secure-password"
}
```

Login returns a response like:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

Send the token on each employee request using the header
`Authorization: Bearer <access_token>`. Missing, invalid, or expired tokens
return `401 Unauthorized`.

## Employee endpoints

Every employee endpoint requires a valid bearer token.

| Method | Path | Purpose | Success status |
|---|---|---|---|
| `POST` | `/employees` | Create an employee. Duplicate IDs or emails return `409 Conflict`. | `201 Created` |
| `GET` | `/employees` | Retrieve all employees. | `200 OK` |
| `GET` | `/employees/{employee_id}` | Retrieve an employee by ID; missing employees return `404 Not Found`. | `200 OK` |
| `PUT` | `/employees/{employee_id}` | Replace employee details; body ID must match URL ID. | `200 OK` |
| `DELETE` | `/employees/{employee_id}` | Delete an employee; missing employees return `404 Not Found`. | `200 OK` |

Example employee body for `POST /employees` and `PUT /employees/1`:

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

Employee email addresses must be valid; name, department, and designation
cannot be blank; and salary must be greater than zero. Invalid request data
returns `422 Unprocessable Entity`. Unexpected database failures are logged and
return a generic `500 Internal Server Error`.

## Try the API with Swagger UI

1. Start the server and open <http://127.0.0.1:8000/docs>.
2. Use **POST /auth/register** to create an account.
3. Use **POST /auth/login** with that account's credentials.
4. Click **Authorize**, enter the access token (or `Bearer <access_token>` if
   prompted for the full header value), and confirm.
5. Try the employee CRUD endpoints. Swagger will send the bearer token for
   protected operations.

## Run automated tests

Install the requirements, then run:

```powershell
python -m pytest
```

The test fixtures select an in-memory SQLite database and a test-only JWT key,
so the tests do not alter the development `employee.db` or use its signing key.
The tests cover registration, login, invalid credentials, token protection,
employee CRUD, not-found responses, and invalid input.
