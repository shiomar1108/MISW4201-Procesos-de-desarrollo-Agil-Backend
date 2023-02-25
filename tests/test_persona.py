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
        users = db.session.query(Usuario).all()
        for user in users:
            db.session.delete(user)
            db.session.commit()
        personas = db.session.query(Persona).all()
        for persona in personas:
            db.session.delete(persona)
            db.session.commit()

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
        self.assertEqual(
            lista_personas[0]["apellido"], nueva_persona["apellido"])

    # Función que valida que no se puedan crear dos entrenadores con el mismo usuario
    def test_crear_entrenadores_mismo_usuario(self):
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
        # Se genera el consumo del API para la creacion del nuevo entrenador
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
        # Se genera el consumo del API para la creacion de un entrenador con un usuario existente
        solicitud_creacion_nuevo = self.client.post("/signin",
                                                    data=json.dumps(nueva_persona),
                                                    headers={"Content-Type": "application/json"})
        # Se obtiene la respuesta de la creacion del entrenador
        self.assertEqual(solicitud_creacion_nuevo.status_code, 409)



    # Función que permite crear un entrenador nuevo
    def test_login_entrenador(self):
        # Se generan los datos para crear el entrenador
        nombre_entrenador = self.data_factory.name()
        apellido_entrenador = self.data_factory.name()
        usuario = "test_" + self.data_factory.name()
        rol = "ENT"
        contrasena = "T1$" + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(
            contrasena.encode("utf-8")).hexdigest()
        # Se forma la esctructura del request
        nueva_persona = {
            "nombre": nombre_entrenador,
            "apellido": apellido_entrenador,
            "usuario": usuario,
            "contrasena": contrasena_encriptada,
            "rol": rol
        }
        # Se genera el consumo del API para la creacion del nuevo entrenador
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
        # Se genera el consumo del API para la creacion de un entrenador con un usuario existente
        solicitud_creacion_nuevo = self.client.post("/signin",
                                                    data=json.dumps(nueva_persona),
                                                    headers={"Content-Type": "application/json"})
        # Se obtiene la respuesta de la creacion del entrenador
        self.assertEqual(solicitud_creacion_nuevo.status_code, 409)

        
        # Se Crea objeto login request
        nueva_login = {
            "usuario": usuario,
            "contrasena": contrasena_encriptada
        }

        # Se genera el consumo del API para login del entrenador
        solicitud_login = self.client.post("/login",
                                              data=json.dumps(nueva_login),
                                              headers={"Content-Type": "application/json"})
        # Se obtiene la respuesta de la creacion del usuario
        respuesta_login = json.loads(solicitud_login.get_data())
        # Se verifica si petición de creacion del entrenador y usuario fue exitosa
        self.assertEqual(solicitud_login.status_code, 200)
        # Se obtienen los datos de login
        login_id = respuesta_login["id"]
        login_mensaje = respuesta_login["mensaje"]
        login_rol = respuesta_login["rol"]
        
        # se compara login y rol
        self.assertEqual(usuario_id,login_id)
        self.assertEqual("Inicio de sesión exitoso", login_mensaje)
        self.assertEqual(rol, login_rol)
