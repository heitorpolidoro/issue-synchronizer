import json
from http.server import BaseHTTPRequestHandler


# noinspection PyPep8Naming
class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        print(self.path)
        print(self.__dict__)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('Hello, world!\n'.encode('utf-8'))
        for k, v in self.__dict__.items():
            self.wfile.write(f"{k}={v}\n".encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        payload = json.loads(body)

        # handle payload here
        print(payload)

        self.send_response(201)
        self.end_headers()
