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


class UserRegister(BaseModel):
    """Request body for creating a user account."""

    username: str
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def username_cannot_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Username cannot be empty.")
        return cleaned_value


class UserLogin(BaseModel):
    """Request body for logging in with an email and password."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Public user information returned by registration."""

    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """JWT access token returned after a successful login."""

    access_token: str
    token_type: str = "bearer"
