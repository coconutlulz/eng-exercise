import logging
import os

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", 6379)
LOG_LEVEL = os.getenv("LOG_LEVEL", logging.DEBUG)
