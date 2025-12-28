import os
import sys


def main() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO")
    concurrency = os.getenv("CELERY_CONCURRENCY", "1")
    args = [
        "celery",
        "-A",
        "src.app.infrastructure.celery.app:celery_app",
        "worker",
        "-l",
        log_level,
        "--concurrency",
        concurrency,
    ]
    os.execvp(args[0], args)


if __name__ == "__main__":
    main()
