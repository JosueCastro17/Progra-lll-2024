from urllib import parse
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import crud_academico
from decimal import Decimal

crudProductos = crud_academico.crud_academico()

# Función personalizada para convertir objetos a un formato serializable
def convertir_a_serializable(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # Convertir Decimal a float para JSON
    raise TypeError(f"Tipo no serializable: {type(obj)}")

class servidorBasico(SimpleHTTPRequestHandler):
    def do_GET(self):
        url_parseada = urlparse(self.path)
        path = url_parseada.path
        query_params = parse_qs(url_parseada.query)

        if path == '/':
            # Sirve la página principal
            self.path = '/principal.html'
            return SimpleHTTPRequestHandler.do_GET(self)

        elif path == '/principal':
            # Obtiene los productos desde la base de datos o uno específico si se proporciona un ID
            try:
                if 'id' in query_params:
                    # Obtener un producto específico por su ID
                    id_producto = query_params['id'][0]
                    productos = crudProductos.consultar()
                    producto = next((p for p in productos if p["id"] == int(id_producto)), None)
                    if producto:
                        respuesta = json.dumps(producto, default=convertir_a_serializable)
                    else:
                        self.send_response(404)
                        self.end_headers()
                        self.wfile.write(b"Producto no encontrado")
                        return
                else:
                    # Obtener todos los productos
                    productos = crudProductos.consultar()
                    respuesta = json.dumps(productos, default=convertir_a_serializable)

                # Configurar la respuesta HTTP
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(respuesta.encode('utf-8'))
            except ConnectionAbortedError:
                print("La conexión fue cerrada por el cliente.")
            except Exception as e:
                print(f"Ocurrió un error inesperado: {e}")
        else:
            # Ruta no encontrada
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Ruta no encontrada")

    def do_POST(self):
        longitud = int(self.headers['Content-Length'])
        body = self.rfile.read(longitud)
        
        try:
            datos = json.loads(body.decode('utf-8'))
            if self.path == '/login':
                # Verificar si el usuario existe en la base de datos
                usuario = datos.get("usuario")
                clave = datos.get("clave")
                if usuario and clave:
                    if crudProductos.login(usuario, clave):
                        # Credenciales correctas, enviar respuesta de éxito
                        self.send_response(200)  # 200 OK
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True, "redirect": "/principal.html"}).encode('utf-8'))
                    else:
                        # Credenciales incorrectas
                        self.send_response(401)  # 401 Unauthorized
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "message": "Credenciales incorrectas"}).encode('utf-8'))
                else:
                    self.send_response(400)  # 400 Bad Request
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "message": "Faltan datos de usuario o clave"}).encode('utf-8'))
            elif self.path == '/principal':
                resp = {"msg": crudProductos.administrar(datos)}

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode('utf-8'))
            elif self.path == '/eliminar':
                resp = {"msg": crudProductos.eliminar(datos["idUsuario"])}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode('utf-8'))
            elif self.path == '/modificar':
                resp = {"msg": crudProductos.modificar(datos["idUsuario"], datos)}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Ruta no encontrada")
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error en el formato del JSON")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Error interno del servidor")

server = HTTPServer(('localhost', 3000), servidorBasico)
print("Servidor ejecutado en el puerto 3000")
server.serve_forever()

