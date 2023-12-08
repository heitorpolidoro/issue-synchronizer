from http.server import HTTPServer

from api.index import Handler


def run():
    server_address = ('127.0.0.1', 3000)
    httpd = HTTPServer(server_address, Handler)
    print('running server on port 3000...')
    httpd.serve_forever()

run()
