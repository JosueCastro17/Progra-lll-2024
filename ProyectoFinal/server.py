from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import crud_BD

# Inicializar la base de datos
crudBD = crud_BD.crud_BD()

# Asegúrate de que el directorio 'imagenes' exista
if not os.path.exists('imagenes'):
    os.makedirs('imagenes')

app = Flask(__name__)

# Ruta para el menú principal
@app.route('/')
def menu_principal():
    return render_template('menuPrincipal.html')  # Usa render_template en lugar de send_static_file

# Ruta para publicaciones
@app.route('/publicaciones')
def publicaciones():
    return render_template('publicaciones.html')  # Usa render_template en lugar de send_static_file

# Ruta para obtener las publicaciones en formato JSON
@app.route('/get_publicaciones')
def get_publicaciones():
    publicaciones = crudBD.consultar()  # Obtener todas las publicaciones
    return jsonify(publicaciones)

# Ruta para servir imágenes
@app.route('/imagenes/<path:filename>')
def imagenes(filename):
    return send_from_directory('imagenes', filename)

@app.route('/EllenImagen/<path:filename>')
def ellen_imagen(filename):
    return send_from_directory('EllenImagen', filename)

# Ruta para manejar el envío de publicaciones
@app.route('/subir_publicacion', methods=['POST'])
def subir_publicacion():
    nombre_vehiculo = request.form.get('nombre_vehiculo')
    precio = request.form.get('precio')
    descripcion = request.form.get('descripcion')
    comentario = request.form.get('Comentario')

    img_file1 = request.files.get('imgVehiculo')
    img_file2 = request.files.get('imgVehiculo2')

    # Validación de campos obligatorios
    if not (nombre_vehiculo and precio and descripcion and img_file1):
        return jsonify({'error': 'Faltan datos o imágenes requeridos'}), 400

    # Guardar las imágenes en el servidor
    img_filename1 = f"{nombre_vehiculo.replace(' ', '_')}_1.jpg"
    img_file1.save(os.path.join('imagenes', img_filename1))

    img_filename2 = None
    if img_file2:
        img_filename2 = f"{nombre_vehiculo.replace(' ', '_')}_2.jpg"
        img_file2.save(os.path.join('imagenes', img_filename2))

    # Insertar el registro en la base de datos
    datos = {
        'nombre_vehiculo': nombre_vehiculo,
        'precio': precio,
        'descripcion': descripcion,
        'Comentario': comentario,
        'imgVehiculo': img_filename1,
        'imgVehiculo2': img_filename2 if img_filename2 else ''
    }
    resp = crudBD.insertar_vehiculo(datos)

    return jsonify({'msg': resp})

# Ruta para agregar un comentario
@app.route('/agregar_comentario', methods=['POST'])
def agregar_comentario():
    data = request.get_json()
    id_publicacion = data.get('id_publicacion')
    comentario = data.get('comentario')

    if not (id_publicacion and comentario):
        return jsonify({'error': 'Faltan datos para el comentario'}), 400

    try:
        crudBD.agregar_comentario(id_publicacion, comentario)
    except Exception as e:
        return jsonify({'error': f'Error al agregar comentario: {str(e)}'}), 500

    return jsonify({'msg': 'Comentario agregado exitosamente'})

# Ruta para editar un comentario
@app.route('/editar_comentario', methods=['POST'])
def editar_comentario():
    data = request.get_json()
    id_comentario = data.get('id_comentario')
    nuevo_comentario = data.get('nuevo_comentario')

    if not (id_comentario and nuevo_comentario):
        return jsonify({'error': 'Faltan datos para editar el comentario'}), 400

    try:
        crudBD.editar_comentario(id_comentario, nuevo_comentario)
    except Exception as e:
        return jsonify({'error': f'Error al editar comentario: {str(e)}'}), 500

    return jsonify({'msg': 'Comentario editado exitosamente'})

# Ruta para eliminar un comentario
@app.route('/eliminar_comentario', methods=['POST'])
def eliminar_comentario():
    data = request.get_json()
    id_comentario = data.get('id_comentario')

    if not id_comentario:
        return jsonify({'error': 'Faltan datos para eliminar el comentario'}), 400

    try:
        crudBD.eliminar_comentario(id_comentario)
    except Exception as e:
        return jsonify({'error': f'Error al eliminar comentario: {str(e)}'}), 500

    return jsonify({'msg': 'Comentario eliminado exitosamente'})

# Iniciar el servidor Flask
if __name__ == '__main__':
    app.run(host='localhost', port=3001)