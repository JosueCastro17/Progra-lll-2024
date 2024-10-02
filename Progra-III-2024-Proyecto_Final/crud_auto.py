import crud_proyectofinal

db = crud_proyectofinal.crud()

class crud_auto:
    def __init__(self):
        self.db = crud_proyectofinal.crud()  # Inicializa self.db como una instancia de la clase crud
    
    # CRUD para los usuarios:
    def consultar(self):
        return self.db.consultar("SELECT * FROM users")
    
    def InsertarUsuario(self, datos):
        try:
            sql = """
                INSERT INTO users (username, password, NombreCompleto, NumeroTelefono)
                VALUES (%s, %s, %s, %s) 
            """
            valores = (datos["username"], datos["password"], datos["NombreCompleto"], datos["NumeroTelefono"])
            return self.db.procesar_consultas(sql, valores)
        except Exception as e:
            return str(e)
    
    def obtener_usuario_por_id(self, user_id):
        sql = """
            SELECT user_id, username, NombreCompleto, NumeroTelefono, imgPerfilUsuario, imgFondoUsuario 
            FROM users 
            WHERE user_id = %s
        """
        valores = (user_id,)
        resultados = self.db.consultar(sql, valores)
        return resultados[0] if resultados else None  # Devuelve el primer resultado o None

    def actualizar_usuario(self, user_id, username, telefono, imgPerfilUsuario=None, imgFondoUsuario=None):
        sql = "UPDATE users SET username = %s, NumeroTelefono = %s"
        valores = [username, telefono]

        if imgPerfilUsuario is not None:
            sql += ", imgPerfilUsuario = %s"
            valores.append(imgPerfilUsuario)

        if imgFondoUsuario is not None:
            sql += ", imgFondoUsuario = %s"
            valores.append(imgFondoUsuario)

        sql += " WHERE user_id = %s"
        valores.append(user_id)

        return self.db.procesar_consultas(sql, valores)
    
    # CRUD para las publicaciones:
    def consultar_publicacion(self):
        return self.db.consultar("SELECT * FROM publicacion_vehiculos")

    def insertar_vehiculo(self, datos):
        sql = """
            INSERT INTO publicacion_vehiculos (nombre_vehiculo, precio, descripcion, imgVehiculo, imgVehiculo2, latitud, longitud, maps_url, map_image, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            datos["nombre_vehiculo"], 
            datos["precio"], 
            datos["descripcion"], 
            datos["imgVehiculo"], 
            datos["imgVehiculo2"],  
            datos["latitud"],  
            datos["longitud"],  
            datos["maps_url"], 
            datos["map_image"],  
            datos["user_id"]
        )
        return self.db.procesar_consultas(sql, valores)

    def agregar_comentario(self, id_publicacion, comentario):
        sql = """
            INSERT INTO comentario_publicacion (id_publicacion, Comentario)
            VALUES (%s, %s)
        """
        valores = (id_publicacion, comentario)
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

    def consultar_vehiculos(self):
        sql = """
            SELECT pv.*, 
                   pv.map_image,
                   u.NombreCompleto,
                   (SELECT GROUP_CONCAT(c.Comentario SEPARATOR '||') 
                    FROM comentario_publicacion c 
                    WHERE pv.Id_Publicacion = c.id_publicacion) AS Comentarios,
                   (SELECT GROUP_CONCAT(c.Id_Comentario SEPARATOR '||') 
                    FROM comentario_publicacion c 
                    WHERE pv.Id_Publicacion = c.id_publicacion) AS Id_Comentarios,
                   (SELECT GROUP_CONCAT(DATE_FORMAT(c.Fecha, '%Y-%m-%d %H:%i:%s') SEPARATOR '||') 
                    FROM comentario_publicacion c 
                    WHERE pv.Id_Publicacion = c.id_publicacion) AS Fechas,
                   (SELECT COUNT(l.user_id) 
                    FROM likes l 
                    WHERE pv.Id_Publicacion = l.Id_Publicacion) AS total_likes
            FROM publicacion_vehiculos pv
            LEFT JOIN users u ON pv.user_id = u.user_id
            ORDER BY pv.Id_Publicacion DESC
        """
        resultados = self.db.consultar(sql)
        print(resultados)  # Para depuración
        return resultados

    def dar_like(self, user_id, Id_Publicacion):
        sql = """
            INSERT INTO likes (user_id, Id_Publicacion, like_status) 
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE like_status = 1;
        """
        valores = (user_id, Id_Publicacion)
        return self.db.procesar_consultas(sql, valores)

    def quitar_like(self, user_id, Id_Publicacion):
        sql = """
            DELETE FROM likes
            WHERE user_id = %s AND Id_Publicacion = %s;
        """
        valores = (user_id, Id_Publicacion)
        return self.db.procesar_consultas(sql, valores)

    def contar_likes(self, Id_Publicacion):
        sql = """
            SELECT COUNT(*) AS total_likes
            FROM likes
            WHERE Id_Publicacion = %s;
        """
        valores = (Id_Publicacion,)
        resultados = self.db.consultar(sql, valores)
        return resultados[0]['total_likes'] if resultados else 0

    def verificar_like(self, user_id, Id_Publicacion):
        sql = """
            SELECT COUNT(*) AS like_exists
            FROM likes
            WHERE user_id = %s AND Id_Publicacion = %s;
        """
        valores = (user_id, Id_Publicacion)
        resultados = self.db.consultar(sql, valores)
        return resultados[0]['like_exists'] > 0 if resultados else False
