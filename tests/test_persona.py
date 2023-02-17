import json
import hashlib
# Se realiza la importación de las dependencias
from unittest import TestCase
from faker import Faker
from faker.generator import random
from modelos import db, Usuario, Persona, PersonaSchema
from app import app

# Clase que contiene las pruebas unitarias asociadas a la entidad Persona


class TestPersona(TestCase):

    # Función que permite realizar la configuración inicial para ejecutar las pruebas
    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        self.persona_schema = PersonaSchema()
        self.usuarios_creados = []

    # Función que permite realizar el proceso de limpieza de las pruebas realizadas
    def tearDown(self):
        pass

    # Función que permite crear un entrenador nuevo
    def test_crear_entrenador(self):
        # Se generan los datos para crear el entrenador
        nombre_entrenador = self.data_factory.name()
        apellido_entrenador = self.data_factory.name()
        usuario = "test_" + self.data_factory.name()
        contrasena = "T1$" + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(
            contrasena.encode("utf-8")).hexdigest()
        # Se forma la esctructura del request
        nueva_persona = {
            "nombre": nombre_entrenador,
            "apellido": apellido_entrenador,
            "usuario": usuario,
            "contrasena": contrasena_encriptada,
            "rol": "ENT"
        }
        # Se genera el consumo del API para la creacion del entrenador
        solicitud_creacion = self.client.post("/signin",
                                              data=json.dumps(nueva_persona),
                                              headers={"Content-Type": "application/json"})
        # Se obtiene la respuesta de la creacion del usuario
        respuesta_creacion = json.loads(solicitud_creacion.get_data())
        # Se verifica si petición de creacion del entrenador y usuario fue exitosa
        self.assertEqual(solicitud_creacion.status_code, 200)
        # Se obtiene el id del usuario creado
        usuario_id = respuesta_creacion["id"]
        self.usuarios_creados.append(usuario_id)
        # Se consulta la persona con base al id de usuario
        persona_consultada = Persona.query.filter_by(usuario=usuario_id)
        lista_personas = [self.persona_schema.dump(
            persona) for persona in persona_consultada]
        # Se obtiene el id del entrenador
        self.entrenador_id = lista_personas[0]["id"],
        # Se valida que la informacion del entrenador haya quedado registrada
        self.assertEqual(lista_personas[0]["nombre"], nueva_persona["nombre"])
        self.assertEqual(lista_personas[0]["apellido"], nueva_persona["apellido"])
