import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeUpdate

logger = logging.getLogger(__name__)


def _commit_changes(db: Session) -> None:
    """Save a change and turn database constraint violations into HTTP 409s."""
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this ID or email already exists",
        ) from error
    except SQLAlchemyError:
        db.rollback()
        raise


def create_employee(db: Session, employee_data: EmployeeCreate) -> Employee:
    """Create an employee, checking the unique ID and email first."""
    if db.get(Employee, employee_data.employee_id) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this ID already exists",
        )

    existing_email = db.scalar(
        select(Employee).where(Employee.email == str(employee_data.email))
    )
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this email already exists",
        )

    employee = Employee(**employee_data.model_dump())
    db.add(employee)
    _commit_changes(db)
    db.refresh(employee)
    return employee


def get_employees(db: Session) -> list[Employee]:
    """Return all employees from the database."""
    return list(db.scalars(select(Employee)).all())


def get_employee(db: Session, employee_id: int) -> Employee:
    """Find one employee or return HTTP 404."""
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    return employee


def update_employee(
    db: Session,
    employee_id: int,
    employee_data: EmployeeUpdate,
) -> Employee:
    """Replace an employee's fields while preserving its URL ID."""
    employee = get_employee(db, employee_id)
    if employee_data.employee_id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The employee ID in the request body must match the URL",
        )

    existing_email = db.scalar(
        select(Employee).where(
            Employee.email == str(employee_data.email),
            Employee.employee_id != employee_id,
        )
    )
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this email already exists",
        )

    for field, value in employee_data.model_dump().items():
        setattr(employee, field, value)

    _commit_changes(db)
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee_id: int) -> None:
    """Delete an employee, returning HTTP 404 if the ID does not exist."""
    employee = get_employee(db, employee_id)
    db.delete(employee)
    _commit_changes(db)
