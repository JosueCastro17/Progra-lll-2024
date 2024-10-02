import crud_conexion

class crud_BD:
    def __init__(self):
        self.db = crud_conexion.crud()

    def consultar_publicacion(self):
        return self.db.consultar("SELECT * FROM publicacion_vehiculos")

    def insertar_vehiculo(self, datos):
        sql = """
            INSERT INTO publicacion_vehiculos (nombre_vehiculo, precio, descripcion, imgVehiculo, imgVehiculo2, latitud, longitud, maps_url, map_image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (datos["nombre_vehiculo"], datos["precio"], datos["descripcion"], datos["imgVehiculo"], datos["imgVehiculo2"],  datos["latitud"],  datos["longitud"],  datos["maps_url"], datos["map_image"])
        return self.db.procesar_consultas(sql, valores)

    def agregar_comentario(self, id_publicacion, comentario):
        sql = """
            INSERT INTO comentario_publicacion (id_publicacion, Comentario)
            VALUES (%s, %s)
        """
        valores = (id_publicacion, comentario)
        print(id_publicacion,comentario)
        return self.db.procesar_consultas(sql, valores)

    def editar_comentario(self, id_comentario, nuevo_comentario):
        sql = """
            UPDATE comentario_publicacion
            SET Comentario = %s
            WHERE Id_Comentario = %s
        """
        valores = (nuevo_comentario, id_comentario)
        return self.db.procesar_consultas(sql, valores)

    def eliminar_comentario(self, id_comentario):
        sql = """
            DELETE FROM comentario_publicacion
            WHERE Id_Comentario = %s
        """
        valores = (id_comentario,)
        return self.db.procesar_consultas(sql, valores)

    def consultar(self):
        sql = """
    SELECT pv.*, 
           pv.map_image,
           GROUP_CONCAT(c.Comentario SEPARATOR '||') AS Comentarios,
           GROUP_CONCAT(c.Id_Comentario SEPARATOR '||') AS Id_Comentarios,
           GROUP_CONCAT(DATE_FORMAT(c.Fecha, '%Y-%m-%d %H:%i:%s') SEPARATOR '||') AS Fechas
    FROM publicacion_vehiculos pv
    LEFT JOIN comentario_publicacion c ON pv.Id_Publicacion = c.id_publicacion
    GROUP BY pv.Id_Publicacion
    """
        resultados = self.db.consultar(sql)
        print(resultados)  # Agrega esta línea
        return resultados



