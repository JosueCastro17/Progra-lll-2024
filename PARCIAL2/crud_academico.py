import crud_conexion
db = crud_conexion.crud()

class crud_academico:
    def consultar(self):
        return db.consultar("SELECT * FROM usuario")
    
    def administrar(self, datos):    
        sql = """
            INSERT INTO usuario (usuario, clave, nombre, direccion, telefono)
            VALUES (%s, %s, %s, %s, %s) 
        """
        valores = (datos["usuario"],  datos["clave"], datos["nombre"], datos["direccion"], datos["telefono"])
        return db.procesar_consultas(sql, valores)
    
    def eliminar(self, id):
        sql = "DELETE FROM usuario WHERE idUsuario = %s"
        valores = (id,)
        return db.procesar_consultas(sql, valores)
    
    def modificar(self, id, datos):
        sql = """
            UPDATE usuario
            SET usuario = %s, clave = %s, nombre = %s, direccion = %s, telefono = %s
            WHERE idUsuario = %s
        """
        valores = (datos["usuario"],  datos["clave"], datos["nombre"], datos["direccion"], datos["telefono"], id)
        return db.procesar_consultas(sql, valores)
    
    def login(self, usuario, clave):
        sql = "SELECT * FROM usuario WHERE usuario = %s AND clave = %s"
        valores = (usuario, clave)
        # Ejecutar la consulta directamente usando un cursor
        with db.conexion.cursor() as cursor:
            cursor.execute(sql, valores)
            resultado = cursor.fetchall()
        return len(resultado) > 0  # Retorna True si el usuario existe, de lo contrario False
