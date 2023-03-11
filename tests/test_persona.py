import json
import hashlib
# Se realiza la importación de las dependencias
from unittest import TestCase
from faker import Faker
from datetime import datetime
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
        contrasena = self.data_factory.password(length=10, special_chars=False, upper_case=True, lower_case= True, digits= True)
        # Se forma la esctructura del request
        nueva_persona = {
            "nombre": nombre_entrenador,
            "apellido": apellido_entrenador,
            "usuario": usuario,
            "contrasena": contrasena,
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
        contrasena = self.data_factory.password(length=10, special_chars=False, upper_case=True, lower_case= True, digits= True)
        # Se forma la esctructura del request
        nueva_persona = {
            "nombre": nombre_entrenador,
            "apellido": apellido_entrenador,
            "usuario": usuario,
            "contrasena": contrasena,
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
        contrasena = self.data_factory.password(length=10, special_chars=False, upper_case=True, lower_case= True, digits= True)
        # Se forma la esctructura del request
        nueva_persona = {
            "nombre": nombre_entrenador,
            "apellido": apellido_entrenador,
            "usuario": usuario,
            "contrasena": contrasena,
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
            "contrasena": contrasena
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

    # Función que permite crear un cliente nuevo
    def test_crear_cliente(self):
        # Se generan los datos para crear el entrenador
        usuario = "test_" + self.data_factory.first_name()
        contrasena = self.data_factory.password(length=10, special_chars=False, upper_case=True, lower_case= True, digits= True)        # Se forma la esctructura del request
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
        # Se verifica si petición de creacion del entrenador y usuario fue exitosa
        self.assertEqual(solicitud_creacion_cliente.status_code, 200)
        # Se obtiene la respuesta de la creacion del usuario
        respuesta_creacion = json.loads(solicitud_creacion_cliente.get_data())
        # Se obtiene el id del usuario creado
        self.assertEqual(nombre_cliente, respuesta_creacion["nombre"])
        self.assertEqual(apellido_cliente, respuesta_creacion["apellido"])
        self.assertEqual(talla_cliente, int(float(respuesta_creacion["talla"])))
        self.assertEqual(peso_cliente, int(float(respuesta_creacion["peso"])))
        self.assertEqual(edad_cliente, int(float(respuesta_creacion["edad"])))
        self.assertEqual(ingreso_cliente, respuesta_creacion["ingreso"])
        self.assertEqual(brazo_cliente, int(float(respuesta_creacion["brazo"])))
        self.assertEqual(pecho_cliente, int(float(respuesta_creacion["pecho"])))
        self.assertEqual(cintura_cliente, int(float(respuesta_creacion["cintura"])))
        self.assertEqual(pierna_cliente, int(float(respuesta_creacion["pierna"])))