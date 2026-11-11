from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class EmployeeFields(BaseModel):
    """Validated employee fields shared by API request schemas."""

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


class EmployeeCreate(EmployeeFields):
    """Request body for creating an employee."""

    employee_id: int


class EmployeeUpdate(EmployeeCreate):
    """Request body for replacing an employee's details."""


class EmployeeResponse(EmployeeCreate):
    """Response schema that reads values from a SQLAlchemy model."""

    model_config = ConfigDict(from_attributes=True)
