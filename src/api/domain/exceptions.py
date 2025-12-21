class TaskNotFoundError(Exception):
    """Raised when a task identifier does not exist in the task backend."""
    def __init__(self, task_id: str) -> None:
        super().__init__(f"Task with id '{task_id}' was not found.")
        self.task_id = task_id


class TaskResultUnavailableError(Exception):
    """Raised when a task exists but its result is not yet available."""

    def __init__(self, task_id: str, state: str) -> None:
        super().__init__(
            f"Task result for id '{task_id}' is not available yet (state={state})."
        )
        self.task_id = task_id
        self.state = state
