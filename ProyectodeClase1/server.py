from urllib import parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

class servidorBasico(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Bienvenidos a Progra III".encode())

server = HTTPServer(('localhost', 3000), servidorBasico)
print("Servidor ejecutado en el puerto 3000")
server.serve_forever()
