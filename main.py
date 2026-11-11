from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, field_validator

app = FastAPI(
    title="Employee Management API",
    description="A beginner-friendly API for managing employee records.",
    version="1.0.0",
)


class Employee(BaseModel):
    """Fields required for creating or updating an employee."""

    employee_id: int
    name: str
    email: EmailStr
    department: str
    salary: float = Field(gt=0)
    designation: str

    @field_validator("name", "department", "designation")
    @classmethod
    def fields_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("This field cannot be empty.")
        return cleaned_value


# Records are stored in memory and will be cleared when the application restarts.
employees: list[Employee] = []


def find_employee_index(employee_id: int) -> int:
    """Return an employee's position in the list, or raise a 404 error."""
    for index, employee in enumerate(employees):
        if employee.employee_id == employee_id:
            return index
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Employee not found",
    )


@app.post("/employees", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(employee: Employee) -> Employee:
    """Add an employee unless the ID is already in use."""
    if any(existing.employee_id == employee.employee_id for existing in employees):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An employee with this ID already exists",
        )
    employees.append(employee)
    return employee


@app.get("/employees", response_model=list[Employee])
def get_employees() -> list[Employee]:
    """Return all employees."""
    return employees


@app.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: int) -> Employee:
    """Return one employee by ID."""
    return employees[find_employee_index(employee_id)]


@app.put("/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: int, updated_employee: Employee) -> Employee:
    """Replace an employee's details while keeping their URL and record IDs aligned."""
    employee_index = find_employee_index(employee_id)
    if updated_employee.employee_id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The employee ID in the request body must match the URL",
        )
    employees[employee_index] = updated_employee
    return updated_employee


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int) -> dict[str, str]:
    """Remove an employee and return a confirmation message."""
    employee_index = find_employee_index(employee_id)
    employees.pop(employee_index)
    return {"message": "Employee deleted successfully"}
