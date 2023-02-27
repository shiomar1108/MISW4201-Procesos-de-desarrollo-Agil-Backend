import json
import hashlib

# Se realiza la importación de las dependencias
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
        contrasena = "T1$" + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode("utf-8")).hexdigest()
        # Se forma la esctructura del request
        nueva_persona = {
            "nombre": self.nombre_entrenador,
            "apellido": self.apellido_entrenador,
            "usuario": usuario,
            "contrasena": contrasena_encriptada,
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
            "contrasena": contrasena_encriptada
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
