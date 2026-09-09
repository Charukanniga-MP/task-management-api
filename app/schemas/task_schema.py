"""Pydantic schema for Task validation and data contract.

SOLID Principles Applied:
- Single Responsibility Principle (SRP): Responsible solely for defining task data structure and validation rules.
"""

from pydantic import BaseModel, Field, field_validator


class TaskSchema(BaseModel):
    title: str = Field(..., min_length=1, description="Task title cannot be empty")
    description: str = Field(..., min_length=1, description="Task description cannot be empty")
    status: str = Field(default="pending", description="Task status")
    priority: str = Field(default="medium", description="Task priority")

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not isinstance(value, str) or not value or not value.strip():
            raise ValueError("Title cannot be empty")
        return value.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        if not isinstance(value, str) or not value or not value.strip():
            raise ValueError("Description cannot be empty")
        return value.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = {"pending", "in_progress", "completed"}
        if value not in allowed:
            raise ValueError(f"Invalid status '{value}'. Allowed: {allowed}")
        return value

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        allowed = {"low", "medium", "high"}
        if value not in allowed:
            raise ValueError(f"Invalid priority '{value}'. Allowed: {allowed}")
        return value