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
        pass

    # Función que permite realizar el proceso de limpieza de las pruebas realizadas
    def tearDown(self):
        pass

    # Función que permite crear un entrenador nuevo
    def test_crear_entrenador(self):
        lista_personas = []
        # Se obtiene el id del entrenador
        self.entrenador_id = lista_personas[0]["id"],
        # Se valida que la informacion del entrenador haya quedado registrada
        self.assertEqual(lista_personas[0]["nombre"], "test_user")
        self.assertEqual(lista_personas[0]["apellido"], "test@user619")

    