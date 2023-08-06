import zmq
from aicmder.service import CLIENT_PORT, WORKER_PORT

LRU_READY = "\x01"

context = zmq.Context(1)

frontend = context.socket(zmq.ROUTER) # ROUTER
backend = context.socket(zmq.DEALER) # DEALER
frontend.bind(f"tcp://*:{CLIENT_PORT}") # For clients
backend.bind(f"tcp://*:{WORKER_PORT}")  # For workers

zmq.device(zmq.QUEUE, frontend, backend)

