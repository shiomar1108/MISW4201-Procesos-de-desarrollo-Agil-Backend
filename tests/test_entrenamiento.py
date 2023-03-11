import json
from unittest import TestCase
from faker import Faker
from faker.generator import random
from modelos import db, Usuario, Ejercicio, Entrenamiento
from datetime import datetime
from app import app
from modelos.modelos import Persona


class TestEntrenamiento(TestCase):

    def setUp(self):
        # Instanciamos la librerias a usar
        self.data_factory = Faker()
        self.client = app.test_client()

        # Se generan los datos para crear el entrenador
        nombre_entrenador = self.data_factory.name()
        apellido_entrenador = self.data_factory.name()
        usuario = "test_" + self.data_factory.first_name()
        contrasena = self.data_factory.password(length=10, special_chars=False, upper_case=True, lower_case= True, digits= True)
        # Se forma la esctructura del request
        nueva_persona = {
            "nombre": nombre_entrenador,
            "apellido": apellido_entrenador,
            "usuario": usuario,
            "contrasena": contrasena
        }

        # Se genera el consumo del API para la creacion del nuevo entrenador
        solicitud_creacion = self.client.post("/signin",
                                              data=json.dumps(nueva_persona),
                                              headers={"Content-Type": "application/json"})

        # Se realiza el login con el usuario creado
        usuario_login = {
            "usuario": usuario,
            "contrasena": contrasena
        }
        solicitud_login = self.client.post("/login",
                                           data=json.dumps(usuario_login),
                                           headers={'Content-Type': 'application/json'})
        respuesta_login = json.loads(solicitud_login.get_data())
        self.token = respuesta_login["token"]
        self.usuario_id = respuesta_login["id"]
        self.ejercicios_creados = []
        self.entrenamientos_creados = []

    def tearDown(self):
        # Eliminamos los ejericicios creados en la prueba
        for ejercicio_creado in self.ejercicios_creados:
            ejercicio = Ejercicio.query.get(ejercicio_creado)
            db.session.delete(ejercicio)
            db.session.commit()

        # Eliminamos los entrenamientos creados en la prueba
        for entrenamiento_creado in self.entrenamientos_creados:
            entrenamiento = Entrenamiento.query.get(entrenamiento_creado)
            db.session.delete(entrenamiento)
            db.session.commit()

        # Eliminamos el usuario creado en la prueba
        users = db.session.query(Usuario).all()
        for user in users:
            db.session.delete(user)
            db.session.commit()

        personas = db.session.query(Persona).all()
        for persona in personas:
            db.session.delete(persona)
            db.session.commit()

    def test_listar_entrenamientos(self):
        # Se crean los ejercicios
        for indexEjercicio in range(0, 5):
            nombre_nuevo_ejercicio = self.data_factory.sentence()
            descripcion_nuevo_ejercicio = self.data_factory.sentence()
            video_nuevo_ejercicio = self.data_factory.image_url()
            calorias_nuevo_ejercicio = round(random.uniform(0.1, 0.99), 2)
            ejercicio_nuevo = Ejercicio(nombre=nombre_nuevo_ejercicio,
                                        descripcion=descripcion_nuevo_ejercicio,
                                        video=video_nuevo_ejercicio,
                                        calorias=calorias_nuevo_ejercicio)
            db.session.add(ejercicio_nuevo)
            db.session.commit()

            # Se almacenan los IDs de los ejercicios creados
            self.ejercicios_creados.append(ejercicio_nuevo.id)

        # Creamos los entrenamientos asociados a los ejercicios
        for indexEjercicioCreado in self.ejercicios_creados:
            nuevo_entrenamiento = {
                "ejercicio": indexEjercicioCreado,
                "fecha": datetime.today().strftime('%Y-%m-%d'),
                "tiempo": f"00:{round(random.randint(10, 59), 2)}:{round(random.randint(10, 59), 2)}",
                "repeticiones": random.randint(1, 10)
            }

            # Se realiza la cración de los entrenamientos
            endpoint_entrenamiento = f"/entrenamientos/{self.usuario_id}"
            headers = {'Content-Type': 'application/json',
                       "Authorization": "Bearer {}".format(self.token)}
            resultado_nuevo_entrenamiento = self.client.post(endpoint_entrenamiento,
                                                             data=json.dumps(
                                                                 nuevo_entrenamiento),
                                                             headers=headers)

            # Validamos que la creación sea exitosa
            self.assertEqual(resultado_nuevo_entrenamiento.status_code, 200)

            # Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
            datos_respuesta = json.loads(
                resultado_nuevo_entrenamiento.get_data())
            self.entrenamientos_creados.append(datos_respuesta['id'])

        # Se realiza la consulta de los entrenamientos registrados
        endpoint_entrenamiento = f"/entrenamientos/{self.usuario_id}"
        headers = {'Content-Type': 'application/json',
                   "Authorization": "Bearer {}".format(self.token)}
        resultado_consulta_entrenamientos = self.client.get(
            endpoint_entrenamiento, headers=headers)
        self.assertEqual(resultado_consulta_entrenamientos.status_code, 200)
        # Validamos si los entrenamientos anteriormente creados se encuentran en la lista de entrenamientos
        index = 0
        for item in json.loads(resultado_consulta_entrenamientos.get_data()):
            self.assertTrue(item['id'] == self.entrenamientos_creados[index])
            index += 1

    def registrar_rutina_realizada(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        
        nombre_usuario = 'test_' + self.data_factory.name()
        contrasena = 'Ta1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()

        registrar_entrenamiento = "{'idRutina': '1', 'fecha': '2023-03-02', 'idPersona': '1', 'entrenamientos': [{'tiempo': '00:10:10', 'repeticiones': '3', 'ejercicio': '1'}, {'tiempo': '00:10:10', 'repeticiones': '3', 'ejercicio': '1'}]}"
        
        # Se realiza la consulta de los entrenamientos registrados
        endpoint_entrenamiento = f"/rutinasEntrenamiento"
        headers = {'Content-Type': 'application/json',
                   "Authorization": "Bearer {}".format(self.token)}
        resultado_nueva_rutina = self.client.post(endpoint_entrenamiento, data=json.dumps(registrar_entrenamiento), headers=headers)

        self.assertEqual("proceso exitoso", resultado_nueva_rutina['res'])


