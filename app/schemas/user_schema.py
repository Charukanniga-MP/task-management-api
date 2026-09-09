"""Pydantic schema for User validation and data contract.

SOLID Principles Applied:
- Single Responsibility Principle (SRP): Responsible solely for defining user data structure and validation rules.
"""

from pydantic import BaseModel, Field, field_validator


class UserSchema(BaseModel):
    name: str = Field(..., min_length=1, description="User name cannot be empty")
    email: str = Field(..., min_length=1, description="User email address")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        return value.strip()

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        if not value or "@" not in value:
            raise ValueError("Invalid email format")
        return value.strip()