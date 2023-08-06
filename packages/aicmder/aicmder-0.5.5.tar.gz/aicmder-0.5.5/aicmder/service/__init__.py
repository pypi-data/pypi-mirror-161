import os

if "CMD_CLIENT_PORT" in os.environ:
    CLIENT_PORT = os.environ.get("CMD_CLIENT_PORT")
else:
    CLIENT_PORT = os.getenv("CMD_CLIENT_PORT", 5655)

if "CMD_WORKER_PORT" in os.environ:
    WORKER_PORT = os.environ.get("CMD_WORKER_PORT")
else:
    WORKER_PORT = os.getenv("CMD_WORKER_PORT", 5656)
