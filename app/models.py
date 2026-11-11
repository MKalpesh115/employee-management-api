from sqlalchemy import CheckConstraint, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class shared by SQLAlchemy database models."""


class Employee(Base):
    """Employee table stored in SQLite."""

    __tablename__ = "employees"
    __table_args__ = (CheckConstraint("salary > 0", name="check_salary_positive"),)

    employee_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String, nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    designation: Mapped[str] = mapped_column(String, nullable=False)


class User(Base):
    """Registered API user; passwords are stored only as secure hashes."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
