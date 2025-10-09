# src/worker/compute_pi_task.py
from __future__ import annotations

import time
from src.api.infrastructure.celery.app import celery_app
from src.setup.worker_config import get_worker_settings
from mpmath import mp

_settings = get_worker_settings()

def get_pi(digits: int) -> str:
    mp.dps = digits
    return str(mp.pi)

@celery_app.task(name="compute_pi", bind=True)
def compute_pi(self, payload: dict) -> dict:
    """
    Pi computation task.
    Simulates heavy pi calculation.
    """
    digits : int = payload["digits"]
    pi : str = get_pi(digits)

    for k in range(digits):
        time.sleep(_settings.SLEEP_PER_DIGIT_SEC)
        percent = int((k + 1) / digits)
        self.update_state(state="PROGRESS", meta={"percent": percent,"message": None, "result": None})

    result = {"percent": 1, "message": None, "result": pi}
    return result
