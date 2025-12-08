from pydantic import BaseModel


class TaskProgress(BaseModel):
    current: int | None = None
    total: int | None = None
    percentage: float | None = None
    phase: str | None = None
