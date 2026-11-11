from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import logging

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user, get_secret_key, router as auth_router
from app.crud import (
    create_employee,
    delete_employee,
    get_employee,
    get_employees,
    update_employee,
)
from app.database import engine, get_db
from app.models import User
from app.schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Check configuration and create any missing database tables."""
    get_secret_key()
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Employee Management API",
    description="A beginner-friendly API for managing employee records.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(auth_router)


@app.exception_handler(SQLAlchemyError)
async def handle_database_error(
    request: Request,
    error: SQLAlchemyError,
) -> JSONResponse:
    """Log unexpected database errors and return a safe server error."""
    logger.exception("Database operation failed", exc_info=error)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred"},
    )


@app.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee_endpoint(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EmployeeResponse:
    return create_employee(db, employee)


@app.get("/employees", response_model=list[EmployeeResponse])
def get_employees_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EmployeeResponse]:
    return get_employees(db)


@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee_endpoint(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EmployeeResponse:
    return get_employee(db, employee_id)


@app.put("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee_endpoint(
    employee_id: int,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EmployeeResponse:
    return update_employee(db, employee_id, employee)


@app.delete("/employees/{employee_id}")
def delete_employee_endpoint(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    delete_employee(db, employee_id)
    return {"message": "Employee deleted successfully"}
