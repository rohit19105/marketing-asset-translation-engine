import logging
import os


def setup_logging():
    """
    Configures application-wide console and file logging.

    Creates the required log directory and configures handlers,
    log levels, and formatting for application logs.
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        handlers=[
            # Terminal
            logging.StreamHandler(),

            # File
            logging.FileHandler(
                os.path.join(log_dir, "app.log"),
                encoding="utf-8"
            )
        ]
    )