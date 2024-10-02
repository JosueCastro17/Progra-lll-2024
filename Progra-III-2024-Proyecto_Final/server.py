from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import crud_auto
import random
import json
import pickle
import numpy as np
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download('punkt')
nltk.download('wordnet')
if not os.path.exists('imagenes'):
    os.makedirs('imagenes')

app = Flask(__name__)

lemmatizer = WordNetLemmatizer()

app.secret_key = 'your_secret_key'  # Clave secreta para manejar sesiones

crudAuto = crud_auto.crud_auto()

intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')

# Ruta para el login (será lo primero que se mostrará al acceder a la app)
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
       

        # Verificar usuario en la base de datos
        usuarios = crudAuto.consultar()
        for usuario in usuarios:

            if usuario['username'] == username and usuario['password'] == password:
                session['username'] = username  # Guardamos el usuario en la sesión

                session['NombreCompleto'] = usuario['NombreCompleto']  # Guardamos el usuario en la sesión
                session['user_id'] = usuario['user_id']
                session['NumeroTelefono'] = usuario['NumeroTelefono']
                return redirect(url_for('home'))  # Redireccionamos a la página principal después del login
            
            
           
        
        # Si las credenciales no son correctas
        flash('Usuario o contraseña incorrectos')
        return render_template('login.html')  # Vuelve a mostrar el login con el mensaje de error

    return render_template('login.html')  # Mostrar el formulario de login si es GET

# Página principal que se muestra después de iniciar sesión
@app.route('/home')
def home():
    if 'username' in session:  # Verificamos si el usuario está logueado
        username = session.get('username', 'usuario')
        NombreCompleto = session.get('NombreCompleto', 'usuario')
        NumeroTelefono = session.get('NumeroTelefono', 'usuario')
        user_id = session.get('user_id', 'usuario')
        return render_template('home.html', NombreCompleto=NombreCompleto, NumeroTelefono=NumeroTelefono, username=username, user_id=user_id)  # Mostrar la página principal si está logueado
    else:
        return redirect(url_for('login'))  # Si no está logueado, redirigir al login

@app.route('/logout')
def logout():
    session.pop('username', None)  # Eliminar la sesión del usuario
    return redirect(url_for('login'))  # Redirigir al login

@app.route('/chats')
def chats():
    if 'username' in session:  # Verificamos si el usuario está logueado
        return render_template('chats.html')  # Mostrar la página principal si está logueado
    else:
        return redirect(url_for('login'))  # Si no está logueado, redirigir al login
    
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i]=1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    print("Predicciones:", res)  # Imprime las predicciones para depuración
    max_index = np.where(res == np.max(res))[0][0]
    category = classes[max_index]
    return category

def get_response(tag, intents_json):
    list_of_intents = intents_json['intents']
    result = ""
    for i in list_of_intents:
        if i["tag"] == tag:
            result = random.choice(i['responses'])
            break
    return result

@app.route('/ia', methods=['GET', 'POST'])
def ia():
    if 'username' in session:  # Verificamos si el usuario está logueado
        return render_template('IA.html')  # Mostrar la página de IA si está logueado
    else:
        return redirect(url_for('login'))  # Si no está logueado, redirigir al login

# Ruta para obtener la respuesta del chatbot
@app.route("/get_response", methods=["POST"])
def chatbot_response():
    message = request.json['message']
    ints = predict_class(message)
    res = get_response(ints, intents)
    return jsonify({"response": res})

@app.route('/profile')
def profile():
    user_id = session.get('user_id')  # Obtenemos el user_id de la sesión
    if user_id:
        user = crudAuto.obtener_usuario_por_id(user_id)  # Obtener el usuario desde la base de datos
        if user:
            return render_template('profile.html', user=user)
    # Si no se encuentra el usuario o no hay sesión, redirigir a la página de login u otra página
    return redirect(url_for('login'))




@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    
    if request.method == 'GET':
        user = crudAuto.obtener_usuario_por_id(user_id)
        if user:
            return render_template('edit_profile.html', user=user)
        else:
            return "Usuario no encontrado", 404

    elif request.method == 'POST':
        user = crudAuto.obtener_usuario_por_id(user_id)
        if not user:
            return "Usuario no encontrado", 404

        username = request.form.get('username') or user['username']
        telefono = request.form.get('NumeroTelefono') or user['NumeroTelefono']
       



        # Manejar las imágenes
        profile_picture = request.files.get('profile_picture')
        background_image = request.files.get('background_image')
        

        upload_folder = 'static/imagenes/'
        profile_path = None
        background_path = None

        try:
            if profile_picture:
                profile_filename = secure_filename(profile_picture.filename)
                profile_path = os.path.join(upload_folder, profile_filename)
                profile_picture.save(profile_path)
                profile_path = f'/static/imagenes/{profile_filename}'
                print("Imagen de perfil guardada en:", profile_path)

            if background_image:
                background_filename = secure_filename(background_image.filename)
                background_path = os.path.join(upload_folder, background_filename)
                background_image.save(background_path)
                background_path = f'/static/imagenes/{background_filename}'
                print("Imagen de fondo guardada en:", background_path)

        except Exception as e:
            print("Error al guardar las imágenes:", str(e))
            mensaje = "Ocurrió un error al intentar guardar las imágenes. Intente nuevamente."
            return render_template('edit_profile.html', user=user, mostrar_modal=True, mensaje=mensaje)

        # Actualizar el usuario en la base de datos
        crudAuto.actualizar_usuario(
            user_id,
            username,
            telefono,
            profile_path if profile_picture else None,
            background_path if background_image else None
        )

        # Actualizar los datos del usuario en la sesión
        user['username'] = username
        user['NumeroTelefono'] = telefono
        

            # Asegúrate de actualizar los datos antes de renderizar
        user['imgPerfilUsuario'] = profile_path if profile_path else user.get('imgPerfilUsuario')
        user['imgFondoUsuario'] = background_path if background_path else user.get('imgFondoUsuario')
        print(user)

        mensaje = "Sus datos se actualizaron correctamente."
        return render_template('edit_profile.html', user=user, mostrar_modal=True, mensaje=mensaje)
    
@app.route('/publicaciones_favoritas')
def publicaciones_favoritas():
    return render_template('publicaciones_favoritas.html')

@app.route('/RegistrarseLogin', methods=['GET', 'POST'])
def RegistrarseLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        NombreCompleto = request.form['NombreCompleto']
        NumeroTelefono = request.form['NumeroTelefono']

        usuarios = crudAuto.consultar()

        for usuario in usuarios:
            if usuario['username'] == username:
                flash('El usuario ya existe')
                return render_template('RegistrarseLogin.html')

        # Crear un diccionario con los datos del usuario
        datos_usuario = {
            'username': username,
            'password': password,
            'NombreCompleto': NombreCompleto,
            'NumeroTelefono': NumeroTelefono
        }

        result = crudAuto.InsertarUsuario(datos_usuario)  # Pasar el diccionario a InsertarUsuario

        if result == "ok":
            flash('Usuario registrado exitosamente')
            return redirect(url_for('login'))
        else:
            flash(f'Error al registrar el usuario: {result}')
            return render_template('RegistrarseLogin.html')

    return render_template('RegistrarseLogin.html')



#Codigo para publicaciones: 

@app.route('/publicaciones')
def publicaciones():

    user_id = session.get('user_id', 'usuario')
    return render_template('publicaciones.html', user_id=user_id)  # Usa render_template en lugar de send_static_file

# Ruta para obtener las publicaciones en formato JSON
@app.route('/get_publicaciones')
def get_publicaciones():
    publicaciones = crudAuto.consultar_vehiculos()  # Obtener todas las publicaciones
    return jsonify(publicaciones)

# Ruta para servir imágenes
@app.route('/imagenes/<path:filename>')
def imagenes(filename):
    return send_from_directory('imagenes', filename)

@app.route('/EllenImagen/<path:filename>')
def ellen_imagen(filename):
    return send_from_directory('EllenImagen', filename)

# Ruta para manejar el envío de publicaciones

#aqui voy a comenzar :



@app.route('/subir_publicacion', methods=['POST'])
def subir_publicacion():
    user_id = session['user_id']
    nombre_vehiculo = request.form.get('nombre_vehiculo')
    precio = request.form.get('precio')
    descripcion = request.form.get('descripcion')
    comentario = request.form.get('Comentario')
    
    # Obtener latitud, longitud y URL de Google Maps del formulario
    latitud = request.form.get('latitud')  # Asegúrate de tener este campo en tu formulario HTML
    longitud = request.form.get('longitud')  # Asegúrate de tener este campo en tu formulario HTML
    maps_url = request.form.get('maps_url')  # Asegúrate de tener este campo en tu formulario HTML
    map_image = request.form.get('map_image')  # Asegúrate de tener este campo en tu formulario HTML
    user_id = session.get('user_id')

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
        'imgVehiculo2': img_filename2 if img_filename2 else '',
        'latitud': latitud,  # Asegúrate de que latitud esté definida
        'longitud': longitud,  # Asegúrate de que longitud esté definida
        'maps_url': maps_url, # Asegúrate de que maps_url esté definida
        'map_image': map_image,
        'user_id': user_id
    }

    # Suponiendo que crudBD es una instancia de tu clase crud_BD
    resp = crudAuto.insertar_vehiculo(datos)

    return jsonify({'msg': resp})



# Ruta para agregar un comentario
@app.route('/agregar_comentario', methods=['POST'])
def agregar_comentario():
    data = request.get_json()
    print(f"Datos recibidos: {data}")  # Agregar logging para depuración
    id_publicacion = data.get('id_publicacion')
    comentario = data.get('comentario')

    print(f"ID Publicación: {id_publicacion}, Comentario: {comentario}")  # Agrega esta línea


    if not (id_publicacion and comentario):
        return jsonify({'error': 'Faltan datos para el comentario'}), 400

    try:
        crudAuto.agregar_comentario(id_publicacion, comentario)
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
        crudAuto.editar_comentario(id_comentario, nuevo_comentario)
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
        crudAuto.eliminar_comentario(id_comentario)
    except Exception as e:
        return jsonify({'error': f'Error al eliminar comentario: {str(e)}'}), 500

    return jsonify({'msg': 'Comentario eliminado exitosamente'})


#Likes en las publicaciones:

@app.route('/like/<int:Id_Publicacion>', methods=['POST'])
def like_post(Id_Publicacion):
    user_id = session['user_id']  # Asume que el usuario está logueado y su ID está en la sesión
    like_status = request.json.get('like_status')  # True para dar like, False para quitar like

    # Verificar si el usuario ya ha dado like a esta publicación
    if like_status:
        # Dar like
        crudAuto.dar_like(user_id=user_id, Id_Publicacion=Id_Publicacion)
    else:
        # Quitar like
        crudAuto.quitar_like(user_id=user_id, Id_Publicacion=Id_Publicacion)

    # Retornar el número actualizado de likes
    total_likes = crudAuto.contar_likes(Id_Publicacion)

    return jsonify({'total_likes': total_likes})

# Iniciar el servidor Flask

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002, debug= True)




