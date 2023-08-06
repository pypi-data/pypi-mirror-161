from multiprocessing import Process, Event
import logging
import zmq
import sys
from termcolor import colored
import json
# from .helper import set_logger
from aicmder.common import set_logger, LOG_VERBOSE
import falcon
from aicmder.service import CLIENT_PORT
# 8s for timeout
REQUEST_TIMEOUT = 8000  
REQUEST_RETRIES = 3
SERVER_ENDPOINT = f"tcp://localhost:{CLIENT_PORT}"

verbose = LOG_VERBOSE
logging = set_logger(colored('SERVER_QUEUE', 'magenta'), verbose)


class Client:

    def __init__(self, endpoint=SERVER_ENDPOINT) -> None:
        self.context = zmq.Context()

        logging.info("Connecting to server…")
        self.client = self.context.socket(zmq.REQ)
        self.client.connect(endpoint)

    def send_request(self, request):
        self.client.send(request)

        retries_left = REQUEST_RETRIES
        while True:
            
            if (self.client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0:
                reply = self.client.recv()
                # logging.info("Server replied msg (%s)", reply.decode())
                return reply
            
            retries_left -= 1
            logging.warning("No response from server")
            # Socket is confused. Close and remove it.
            self.client.setsockopt(zmq.LINGER, 0)
            self.client.close()
            if retries_left == 0:
                logging.error("Server seems to be offline, abandoning")
                raise Exception("Server seems to be offline, abandoning")
                # sys.exit()

            logging.info("Reconnecting to server…")
            # Create new connection
            self.client = self.context.socket(zmq.REQ)
            self.client.connect(SERVER_ENDPOINT)
            logging.debug("Resending (%s)", request)
            self.client.send(request)

    def close(self):
        """
            Gently close all connections of the client. 
        """
        self.client.close()
        self.context.term()

class BCManager():
    def __init__(self, available_bc):
        self.available_bc = available_bc
        self.bc = None

    def __enter__(self):
        self.bc = self.available_bc.pop()
        return self.bc

    def __exit__(self, *args):
        self.available_bc.append(self.bc)

class ConcurrentClient:

    def __init__(self, max_concurrency = 500) -> None:
        self.max_concurrency = max_concurrency
        self.available_bc = [Client() for _ in range(max_concurrency)]
        
    def send_request(self, request):
        with BCManager(self.available_bc) as bc:
            return bc.send_request(request)
  

    def close(self):
        for bc in self.available_bc:
            bc.close()





class JSONTranslator:
    # NOTE: Normally you would simply use req.get_media() and resp.media for
    # this particular use case; this example serves only to illustrate
    # what is possible.

    async def process_request(self, req, resp):
        # NOTE: Test explicitly for 0, since this property could be None in
        # the case that the Content-Length header is missing (in which case we
        # can't know if there is a body without actually attempting to read
        # it from the request stream.)
        if req.content_length == 0 or req.method not in ('POST', 'PUT'):
            # Nothing to do
            return

        body = await req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest(title='Empty request body',
                                        description='A valid JSON document is required.')

        try:
            # req.context.doc = json.loads(body.decode('utf-8'))
            req.context.doc = body.decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            description = ('Could not decode the request body. The '
                           'JSON was incorrect or not encoded as '
                           'UTF-8.')

            raise falcon.HTTPBadRequest(title='Malformed JSON',
                                        description=description)

    async def process_response(self, req, resp, resource, req_succeeded):
        if not hasattr(resp.context, 'result'):
            return

        resp.text = json.dumps(resp.context.result)

def max_body(limit):

    async def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPPayloadTooLarge(
                title='Request body is too large', description=msg)

    return hook

class Prediction:

    def __init__(self, concurrent):
        self.concurrent = concurrent

    async def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.content_type = falcon.MEDIA_TEXT  # Default is JSON, so override
        resp.text = ('OK')
        # resp.text = ('\nService status'
        #              '\nI am alive.\n'
        #              '\n'
        #              '    By Faith\n\n')

    
    @falcon.before(max_body(20 * 1024 * 1024))
    async def on_post(self, req, resp):
        result = ''
        try:
            json_str = req.context.doc
            # print('---', json_str)
            # logging.debug(req, json_str)
            if "module" in req.params:
                module_name = req.params["module"]
                json_str = module_name + '\n' + json_str
            else:
                json_str = '\n' + json_str
            result = self.concurrent.send_request(json_str.encode())
            
            if type(result) == bytes:
                # try:
                #     result = json.loads(result.decode('utf-8'))
                # except Exception as e:
                result = result.decode('utf-8')
       
            # print(doc, type(doc), doc['test'])
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(
                title='Missing thing',
                description='A thing must be submitted in the request body.')

        # proper_thing = await self.db.add_thing(doc)
        
        # data = await req.stream.read()
        # resp_content = str(data)
        # print('POST', type(resp_content), type(data), resp_content, '--')
        resp.status = falcon.HTTP_201
        resp.text = result

class HTTPProxy(Process):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.is_ready = Event()

    def create_app(self):
        import falcon.asgi
        app = falcon.asgi.App(middleware=[
            JSONTranslator(),
        ])
        # Resources are represented by long-lived class instances
        prediction = Prediction(self.concurrent)

        # things will handle all requests to the '/things' URL path
        app.add_route('/predict', prediction)
        return app


    @DeprecationWarning
    def create_fastapi_app(self):

        from fastapi import FastAPI, Request
        from flask_json import JsonError

        app = FastAPI()

        # logger = set_logger(colored('PROXY', 'red'), self.args.verbose)

        # @app.get('/status/server')
        # def get_server_status():
        #     return bc.server_status

        # @app.get('/status/client')
        # def get_client_status():
        #     return bc.status

        @app.post('/predict')
        def predict(data: dict, request: Request):
            # data = request.form if request.form else request.json
            try:
                logging.debug(request, data)
                json_str = json.dumps(data)
                # logger.info('new request from %s' % request.client.host)
                result = self.concurrent.send_request(json_str.encode())

                if type(result) == bytes:
                    result = json.loads(result.decode('utf-8'))
                    return result
                print('result--', result)
                return result
            except Exception as e:
                print(e)
                # logger.error('error when handling HTTP request', exc_info=True)
                raise JsonError(description=str(e), type=str(type(e).__name__))

        return app

    def run(self):
        import uvicorn
        from uvicorn.config import LOGGING_CONFIG
        self.concurrent = ConcurrentClient(max_concurrency = self.args.max_connect)
        app = self.create_app()
        self.is_ready.set()
        # LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
        LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
        uvicorn.run(app, host="0.0.0.0", port=self.args.http_port)


if __name__ == "__main__":
    client = Client()
    str = '{"img_base64": "test"}'
    resp = client.send_request(str.encode())
    print(resp)