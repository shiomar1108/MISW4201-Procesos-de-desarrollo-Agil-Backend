import json
import hashlib
from datetime import datetime
from unittest import TestCase
from faker import Faker
from faker.generator import random
from modelos import db, Usuario, Persona, PersonaSchema
from app import app

class TestEntrenadores(TestCase):
    # Función que permite realizar la configuración inicial para ejecutar las pruebas
    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        self.persona_schema = PersonaSchema()
        self.usuarios_creados = []
        # Se generan los datos para crear el entrenador
        self.nombre_entrenador = self.data_factory.name()
        self.apellido_entrenador = self.data_factory.name()
        usuario = "test_" + self.data_factory.name()
        contrasena = self.data_factory.password(length=10, special_chars=False, upper_case=True, lower_case= True, digits= True)
        # Se forma la esctructura del request
        nueva_persona = {
            "nombre": self.nombre_entrenador,
            "apellido": self.apellido_entrenador,
            "usuario": usuario,
            "contrasena": contrasena,
            "rol": "ENT",
        }
        # Se genera el consumo del API para la creacion del entrenador
        solicitud_creacion = self.client.post(
            "/signin",
            data=json.dumps(nueva_persona),
            headers={"Content-Type": "application/json"},
        )
        # Se verifica si petición de creacion del entrenador y usuario fue exitosa
        self.assertEqual(solicitud_creacion.status_code, 200)
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


    # Función que permite realizar el proceso de limpieza de las pruebas realizadas
    def tearDown(self):
        users = db.session.query(Usuario).all()
        for user in users:
            db.session.delete(user)
            db.session.commit()
        personas = db.session.query(Persona).all()
        for persona in personas:
            db.session.delete(persona)
            db.session.commit()

    # Función que permite crear un entrenador nuevo
    def test_get_entrenadores(self):
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_entrenadores = "/entrenadores"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        resultado_consulta_entrenadores = self.client.get(endpoint_entrenadores,
                                                   headers=headers)
        #Obtener los datos de respuesta y dejarlos un objeto json
        datos_respuesta = json.loads(resultado_consulta_entrenadores.get_data())
        #Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
        self.assertEqual(resultado_consulta_entrenadores.status_code, 200)
        self.assertEqual(datos_respuesta[-1]["nombre"], self.nombre_entrenador)
        self.assertEqual(datos_respuesta[-1]["apellido"], self.apellido_entrenador)
        self.assertIsNotNone(datos_respuesta[-1]["id"])

    def test_eliminar_entrenador(self):
        # Se generan los datos para crear el entrenador
        usuario = "test_" + self.data_factory.first_name()
        contrasena = self.data_factory.password(length=10, special_chars=False, upper_case=True, lower_case= True, digits= True)
        # Se forma la esctructura del request
        nueva_entrenador = {
            "nombre": self.data_factory.name(),
            "apellido": self.data_factory.name(),
            "usuario": usuario,
            "contrasena": contrasena
        }
        # Se genera el consumo del API para la creacion del nuevo entrenador
        solicitud_creacion_entrenador = self.client.post("/signin",
                                              data=json.dumps(nueva_entrenador),
                                              headers={"Content-Type": "application/json"})
        # Se verifica si petición de creacion del entrenador y usuario fue exitosa
        self.assertEqual(solicitud_creacion_entrenador.status_code, 200)
        # Se obtiene la respuesta de la creacion del usuario
        respuesta_creacion_entrenador = json.loads(solicitud_creacion_entrenador.get_data())
        # Se obtiene el id del entrenador creado
        entrenador_id = respuesta_creacion_entrenador["id"]
        # Se realiza el login con el usuario creado
        usuario_login = {
            "usuario": usuario,
            "contrasena": contrasena
        }
        solicitud_login = self.client.post("/login",
                                              data=json.dumps(usuario_login),
                                              headers={"Content-Type": "application/json"})
        # Se verifica si el login fue exitoso
        self.assertEqual(solicitud_login.status_code, 200)
        respuesta_login = json.loads(solicitud_login.get_data())
        token = respuesta_login["token"]
        entrenador_id_login = respuesta_login["id"]
        # Se realiza la eliminación del entrenador
        solicitud_eliminacion = self.client.delete(f"entrenador/{entrenador_id_login}",
                                              headers={"Content-Type": "application/json",
                                                       "Authorization": "Bearer {}".format(token)})
        # Se verifica si la eliminacion del entrenador fue exitosa
        self.assertEqual(solicitud_eliminacion.status_code, 204)
        # Consultamos si el usuario asociado al entrenador existe
        usuario = Usuario.query.get(entrenador_id_login)
        self.assertEqual(usuario, None)
        
    def test_eliminar_entrenador_con_clientes(self):
        # Se generan los datos para crear el entrenador
        usuario = "test_" + self.data_factory.first_name()
        contrasena = self.data_factory.password(length=10, special_chars=False, upper_case=True, lower_case= True, digits= True)
        # Se forma la esctructura del request
        nueva_entrenador = {
            "nombre": self.data_factory.name(),
            "apellido": self.data_factory.name(),
            "usuario": usuario,
            "contrasena": contrasena
        }
        # Se genera el consumo del API para la creacion del nuevo entrenador
        solicitud_creacion_entrenador = self.client.post("/signin",
                                              data=json.dumps(nueva_entrenador),
                                              headers={"Content-Type": "application/json"})
        # Se verifica si petición de creacion del entrenador y usuario fue exitosa
        self.assertEqual(solicitud_creacion_entrenador.status_code, 200)
        # Se obtiene la respuesta de la creacion del usuario
        respuesta_creacion_entrenador = json.loads(solicitud_creacion_entrenador.get_data())
        # Se obtiene el id del entrenador creado
        entrenador_id = respuesta_creacion_entrenador["id"]
        # Se realiza el login con el usuario creado
        usuario_login = {
            "usuario": usuario,
            "contrasena": contrasena
        }
        solicitud_login = self.client.post("/login",
                                              data=json.dumps(usuario_login),
                                              headers={"Content-Type": "application/json"})
        # Se verifica si el login fue exitoso
        self.assertEqual(solicitud_login.status_code, 200)
        respuesta_login = json.loads(solicitud_login.get_data())
        token = respuesta_login["token"]
        entrenador_id_login = respuesta_login["id"]
        # Se forma la esctructura del request para crear un cliente
        nombre_cliente = self.data_factory.name()
        apellido_cliente = self.data_factory.last_name()
        talla_cliente = random.randint(1, 50)
        peso_cliente = random.randint(1, 100)
        edad_cliente = random.randint(1, 40)
        ingreso_cliente = datetime.today().strftime('%Y-%m-%d')
        brazo_cliente = random.randint(1, 30)
        pecho_cliente = random.randint(1, 60)
        cintura_cliente = random.randint(1, 50)
        pierna_cliente = random.randint(1, 30)
        nuevo_cliente = {
            "nombre": nombre_cliente,
            "apellido": apellido_cliente,
            "talla": talla_cliente,
            "peso": peso_cliente,
            "edad": edad_cliente,
            "ingreso": ingreso_cliente,
            "brazo": brazo_cliente,
            "pecho": pecho_cliente,
            "cintura": cintura_cliente,
            "pierna": pierna_cliente,
            "entrenando": "true",
            "razon": "",
            "terminado": "1900-01-01",
            "usuario": "usr_" + self.data_factory.first_name(),
            "contrasena": f"{self.data_factory.last_name()}{random.randint(1, 999)}"
        }
        # Se genera el consumo del API para la creacion del entrenador
        solicitud_creacion_cliente = self.client.post(f"/personas/{entrenador_id}",
                                              data=json.dumps(nuevo_cliente),
                                              headers={"Content-Type": "application/json",
                                                       "Authorization": "Bearer {}".format(token)})
        # Se verifica si petición de creacion del cliente fue exitosa
        self.assertEqual(solicitud_creacion_cliente.status_code, 200)
        # Se realiza la eliminación del entrenador
        solicitud_eliminacion = self.client.delete(f"entrenador/{entrenador_id_login}",
                                              headers={"Content-Type": "application/json",
                                                       "Authorization": "Bearer {}".format(token)})
        # Se verifica si la eliminacion del entrenador fue exitosa
        self.assertEqual(solicitud_eliminacion.status_code, 409)