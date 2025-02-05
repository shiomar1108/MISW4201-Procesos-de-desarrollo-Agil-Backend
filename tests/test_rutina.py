import json
import hashlib
from faker import Faker
import unittest
from modelos import db, Usuario, Rutina, Ejercicio
from app import app
import random

class TestRutina(unittest.TestCase):               

    def setUp(self):
        self.client = app.test_client()        
        self.data_factory = Faker()
        Faker.seed(1000)
        self.data = []
        self.ejercicio = []
        for i in range(0, 10):
            self.data.append((
                self.data_factory.first_name(),
                self.data_factory.sentence(),
                self.data_factory.file_path(depth=3),
                self.data_factory.random_int(1, 10000)
            ))
            self.ejercicio.append(
                Ejercicio(
                    nombre=self.data[-1][0],
                    descripcion=self.data[-1][1],
                    video=self.data[-1][2],
                    calorias=self.data[-1][3]
                ))
            db.session.add(self.ejercicio[-1])
            db.session.commit()
        
    
    def test_crear_rutinas(self):
        self.data_factory = Faker()
        Faker.seed(1000)
        self.data = []
        self.rutina = []
        for i in range(0, 5):
            self.data.append((
                self.data_factory.first_name(),
                self.data_factory.sentence()
            ))
            self.rutina.append(
                Rutina(
                    nombre=self.data[-1][0],
                    descripcion=self.data[-1][1]
                ))
            db.session.add(self.rutina[-1])
            db.session.commit()
        rutinas = db.session.query(Rutina).all()        
        self.assertEqual(len(rutinas), 5)
        
        
    def test_asignar_ejercicio_a_rutina(self):
        self.data_factory = Faker()
        Faker.seed(1000)
        self.data = []
        self.rutina = []
        for i in range(0, 5):
            self.data.append((
                self.data_factory.first_name(),
                self.data_factory.sentence()
            ))
            self.rutina.append(
                Rutina(
                    nombre=self.data[-1][0],
                    descripcion=self.data[-1][1]
                ))
            db.session.add(self.rutina[-1])
            db.session.commit()
        rutinas = db.session.query(Rutina).all()

        for k in range(0, len(rutinas)):            
            rutina = rutinas[k]
            ejercicios = db.session.query(Ejercicio).all()
            for i in range(0, len(ejercicios)):
                rutina.ejercicios.append(ejercicios[i])       
            self.assertEqual(len(ejercicios), len(Rutina.query.all()[k].ejercicios))



    def tearDown(self):
        rutinas = db.session.query(Rutina).all()
        for rutina in rutinas:
            db.session.delete(rutina)
            db.session.commit()
        ejercicios = db.session.query(Ejercicio).all()
        for ejercicio in ejercicios:
            db.session.delete(ejercicio)
            db.session.commit()


class TestRutinaEndPoint(unittest.TestCase):

    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        
        nombre_usuario = 'test_' + self.data_factory.name()
        contrasena = 'Ta1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()
        
        # Se crea el usuario para identificarse en la aplicación
        usuario_nuevo = Usuario(usuario=nombre_usuario, contrasena=contrasena_encriptada)
        db.session.add(usuario_nuevo)
        db.session.commit()

        
        usuario_login = {
            "usuario": nombre_usuario,
            "contrasena": contrasena
        }

        solicitud_login = self.client.post("/login",
                                                data=json.dumps(usuario_login),
                                                headers={'Content-Type': 'application/json'})

        respuesta_login = json.loads(solicitud_login.get_data())

        self.token = respuesta_login["token"]
        self.usuario_id = respuesta_login["id"]
        
        self.rutinas_creadas = []
        
    def tearDown(self):
        rutinas = db.session.query(Rutina).all()
        for rutina in rutinas:
            db.session.delete(rutina)
            db.session.commit()
        ejercicios = db.session.query(Ejercicio).all()
        for ejercicio in ejercicios:
            db.session.delete(ejercicio)
            db.session.commit() 
        usuarios = db.session.query(Usuario).all()           
        for usuario in usuarios:
            db.session.delete(usuario)
            db.session.commit()    

    def test_crear_rutina(self):
        #Crear los datos del ejercicio
        nombre_nueva_rutina = self.data_factory.first_name()
        descripcion_nueva_rutina = self.data_factory.sentence()        
        
        #Crear el json con el ejercicio a crear
        nueva_rutina = {
            "nombre": nombre_nueva_rutina,
            "descripcion": descripcion_nueva_rutina            
        }
        
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_rutinas = "/rutinas"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_nueva_rutina = self.client.post(endpoint_rutinas,
                                                   data=json.dumps(nueva_rutina),
                                                   headers=headers)
                                                   

        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_nueva_rutina.get_data())        
        rutina = Rutina.query.get(datos_respuesta['id'])
        self.rutinas_creadas.append(rutina)
                                                           
        #Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
        self.assertEqual(resultado_nueva_rutina.status_code, 200)
        self.assertEqual(datos_respuesta['nombre'], rutina.nombre)
        self.assertEqual(datos_respuesta['descripcion'], rutina.descripcion)       
        self.assertIsNotNone(datos_respuesta['id'])


    def test_listar_rutinas(self):
        #Crear los datos de las rutinas
        self.data_factory = Faker()
        Faker.seed(1000)
        self.data = []
        self.rutina = []
        for i in range(0, 5):
            self.data.append((
                self.data_factory.first_name(),
                self.data_factory.sentence()
            ))
            self.rutina.append(
                Rutina(
                    nombre=self.data[-1][0],
                    descripcion=self.data[-1][1]
                ))
            db.session.add(self.rutina[-1])
            db.session.commit()
        
               
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_rutinas = "/rutinas"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_consulta_rutina = self.client.get(endpoint_rutinas,
                                                  headers=headers)

        #Obtener los datos de respuesta y dejarlos en un objeto json
        rutinas_respuesta = json.loads(resultado_consulta_rutina.get_data())
        
        #Verificar que el llamado fue exitoso
        self.assertEqual(resultado_consulta_rutina.status_code, 200)

        #Verificar las rutinas creadas con sus datos
        rutinas_creadas = db.session.query(Rutina).all()
        for rutina_creada in rutinas_creadas:
            for rutina_respuesta in rutinas_respuesta:
                if rutina_respuesta['id'] == rutina_creada.id:
                    self.assertEqual(rutina_respuesta['nombre'], rutina_creada.nombre)
                    self.assertEqual(rutina_respuesta['descripcion'], rutina_creada.descripcion)


    def test_dar_rutina(self):
        #Crear los datos de la rutina 
        self.data_factory = Faker()
        Faker.seed(1000)              
        rutina = Rutina(nombre=self.data_factory.first_name(), descripcion=self.data_factory.sentence())
        db.session.add(rutina)
        db.session.commit()        
               
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_rutina = "/rutina/" + str(rutina.id)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_consulta_rutina = self.client.get(endpoint_rutina,
                                                  headers=headers)
                                                  
        #Obtener los datos de respuesta y dejarlos en un objeto json
        rutina_respuesta = json.loads(resultado_consulta_rutina.get_data())
                                                   
        
        #Verificar que el llamado fue exitoso
        self.assertEqual(resultado_consulta_rutina.status_code, 200)

        #Verificar las rutinas creadas con sus datos
        rutina_creada = db.session.query(Rutina).get_or_404(rutina.id)
        self.assertEqual(rutina_respuesta['id'], str(rutina_creada.id))
        self.assertEqual(rutina_respuesta['nombre'], rutina_creada.nombre)
        self.assertEqual(rutina_respuesta['descripcion'], rutina_creada.descripcion)

      
    def test_consultar_rutina(self):
        #Crear los datos del ejercicio
        nombre_nueva_rutina = self.data_factory.first_name()
        descripcion_nueva_rutina = self.data_factory.sentence()        
        
        #Crear el json con el ejercicio a crear
        nueva_rutina = {
            "nombre": nombre_nueva_rutina,
            "descripcion": descripcion_nueva_rutina            
        }
        
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_rutinas = "/rutinas"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_nueva_rutina = self.client.post(endpoint_rutinas,
                                                   data=json.dumps(nueva_rutina),
                                                   headers=headers)                                                   


        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_nueva_rutina.get_data())        
        rutina = Rutina.query.get(datos_respuesta['id'])
        data = []
        ejercicio = []
        for i in range(0, 5):
            data.append((
                self.data_factory.first_name(),
                self.data_factory.sentence(),
                self.data_factory.file_path(depth=3),
                self.data_factory.random_int(1, 10000)
            ))
            ejercicio.append(
                Ejercicio(
                    nombre=data[-1][0],
                    descripcion=data[-1][1],
                    video=data[-1][2],
                    calorias=data[-1][3]
                ))
            db.session.add(ejercicio[-1])
            db.session.commit()


        ejercicios = db.session.query(Ejercicio).all()
        for i in range(0, len(ejercicios)):
            rutina.ejercicios.append(ejercicios[i])
            db.session.commit()
        
        #COnsultar Ejercicios de una Rutina por Servicio
        endpoint_rutinas = "/rutina/" + str(rutina.id)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_consulta_rutina = self.client.get(endpoint_rutinas,                                                  
                                                   headers=headers)

        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta_rutina = json.loads(resultado_consulta_rutina.get_data())        
        rutina = Rutina.query.get(datos_respuesta_rutina['id'])
        self.assertEqual(ejercicios, rutina.ejercicios )

    def test_asociar_ejercicio_a_rutina(self):
        #Crear los datos de la rutina 
        self.data_factory = Faker()
        Faker.seed(1000)              
        rutina = Rutina(nombre=self.data_factory.first_name(), descripcion=self.data_factory.sentence())
        db.session.add(rutina)
        db.session.commit()
        ejercicios_originales = len(rutina.ejercicios)    
        
        self.data = []
        self.ejercicio = []
        for i in range(0, 10):
            self.data.append((
                self.data_factory.first_name(),
                self.data_factory.sentence(),
                self.data_factory.file_path(depth=3),
                self.data_factory.random_int(1, 10000)
            ))
            self.ejercicio.append(
                Ejercicio(
                    nombre=self.data[-1][0],
                    descripcion=self.data[-1][1],
                    video=self.data[-1][2],
                    calorias=self.data[-1][3]
                ))
            db.session.add(self.ejercicio[-1])
            db.session.commit()

        id_rutina = 1
        id_ejercicio = random.randint(1,10)                 
        
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_rutina = "/rutina/" + str(id_rutina) + "/ejercicio/" + str(id_ejercicio)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_asociar_ejercicio = self.client.put(endpoint_rutina,
                                                    headers=headers)
        
        #Obtener los datos de respuesta y dejarlos un objeto json
        datos_asociacion = json.loads(resultado_asociar_ejercicio.get_data())        
         
        #Verificar que el llamado fue exitoso
        self.assertEqual(resultado_asociar_ejercicio.status_code, 200)
        
        rutina_actualizada = db.session.query(Rutina).get(id_rutina)
        #Verificar que la rutina tiene un nuevo ejercicio asociado
        self.assertNotEqual(ejercicios_originales,len(rutina_actualizada.ejercicios))
        
        #verificar que el id del ejercicio asociado es igual al id del ejercicio enviado
        self.assertEqual(datos_asociacion['ejercicios'][0]['id'], str(id_ejercicio))

        #Verificar que no se duplican ejercicios al hacer una nueva llamada
        endpoint_rutina = "/rutina/" + str(id_rutina) + "/ejercicio/" + str(id_ejercicio)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_asociar_ejercicio_repetido = self.client.put(endpoint_rutina,
                                                    headers=headers)

        datos_nueva_asociacion = json.loads(resultado_asociar_ejercicio_repetido.get_data())
        
        self.assertEqual(resultado_asociar_ejercicio_repetido.status_code, 200)
        self.assertEqual(len(datos_nueva_asociacion['ejercicios']), len(datos_asociacion['ejercicios']))
           

    def test_consultar_rutinas_diferentes(self):
        #Crear los datos del ejercicio
        nombre_nueva_rutina = self.data_factory.first_name()
        descripcion_nueva_rutina = self.data_factory.sentence()        
        
        #Crear el json con el ejercicio a crear
        nueva_rutina = {
            "nombre": nombre_nueva_rutina,
            "descripcion": descripcion_nueva_rutina            
        }
        
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_rutinas = "/rutinas"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_nueva_rutina = self.client.post(endpoint_rutinas,
                                                   data=json.dumps(nueva_rutina),
                                                   headers=headers)                                                   

        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_nueva_rutina.get_data())        
        rutina = Rutina.query.get(datos_respuesta['id'])
        data = []
        ejercicio = []
        for i in range(0, 5):
            data.append((
                self.data_factory.first_name(),
                self.data_factory.sentence(),
                self.data_factory.file_path(depth=3),
                self.data_factory.random_int(1, 10000)
            ))

            ejercicio.append(
                Ejercicio(
                    nombre=data[-1][0],
                    descripcion=data[-1][1],
                    video=data[-1][2],
                    calorias=data[-1][3]
                ))            
            db.session.add(ejercicio[-1])
            db.session.commit()


        ejercicios = db.session.query(Ejercicio).all()
        for i in range(0, len(ejercicios)):
            rutina.ejercicios.append(ejercicios[i])
            db.session.commit()

       # agregar ejercicios nos asignados a una rutina
        ejercicio2 = []
        for i in range(0, 1):
            data.append((
                self.data_factory.first_name(),
                self.data_factory.sentence(),
                self.data_factory.file_path(depth=3),
                self.data_factory.random_int(1, 10000)
            ))
            ejercicio2.append(
                Ejercicio(
                    nombre=data[-1][0],
                    descripcion=data[-1][1],
                    video=data[-1][2],
                    calorias=data[-1][3]
                ))
            db.session.add(ejercicio2[-1])
            db.session.commit()

        #COnsultar Ejercicios de una Rutina por Servicio
        endpoint_rutinas_diferentes = "/rutina/" + str(rutina.id) + str("/diferente")
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_consulta_rutina = self.client.get(endpoint_rutinas_diferentes,                                                  
                                                   headers=headers)

        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta_rutina_ejercicios = json.loads(resultado_consulta_rutina.get_data())
        self.assertEqual(len(ejercicio2), len(datos_respuesta_rutina_ejercicios) )


    def test_consulta_rutina_con_3_ejercicios(self):
        #Crear los datos de la rutina 
        self.data_factory = Faker()
        Faker.seed(1000)              
        rutina1 = Rutina(nombre=self.data_factory.first_name(), descripcion=self.data_factory.sentence())
        rutina2 = Rutina(nombre=self.data_factory.first_name(), descripcion=self.data_factory.sentence())
        rutina3 = Rutina(nombre=self.data_factory.first_name(), descripcion=self.data_factory.sentence())
        db.session.add(rutina1)
        db.session.add(rutina2)
        db.session.add(rutina3)
        db.session.commit()
        
        self.data = []
        self.ejercicio = []
        for i in range(0, 20):
            self.data.append((
                self.data_factory.first_name(),
                self.data_factory.sentence(),
                self.data_factory.file_path(depth=3),
                self.data_factory.random_int(1, 10000)
            ))
            self.ejercicio.append(
                Ejercicio(
                    nombre=self.data[-1][0],
                    descripcion=self.data[-1][1],
                    video=self.data[-1][2],
                    calorias=self.data[-1][3]
                ))
            db.session.add(self.ejercicio[-1])
            db.session.commit()

        #Se asocia cantidad aleatoria de ejercicios a rutinas
        #Se asocia menos de 3 ejercicios a Rutina 1 
        id_ejercicios = list(range(1,21))
        totalEjercicios1 = random.randint(0,2)
        id_ejercicios_muestra = random.sample(id_ejercicios, totalEjercicios1)
        for i in range(0, totalEjercicios1):                        
            ejercicio = db.session.query(Ejercicio).get(id_ejercicios_muestra[i])
            rutina1.ejercicios.append(ejercicio)
            db.session.commit()        

        #Se asocia entre 3 y 9 ejercicios a Rutina 2                         
        totalEjercicios2 = random.randint(3,9)
        id_ejercicios_muestra = random.sample(id_ejercicios, totalEjercicios2)
        for i in range(0, totalEjercicios2):                        
            ejercicio = db.session.query(Ejercicio).get(id_ejercicios_muestra[i])
            rutina2.ejercicios.append(ejercicio)
            db.session.commit()        
        
        #Se asocia entre 10 y 20 ejercicios a Rutina 3
        totalEjercicios3 = random.randint(10,20)
        id_ejercicios_muestra = random.sample(id_ejercicios, totalEjercicios3)
        for i in range(0, totalEjercicios3):                        
            ejercicio = db.session.query(Ejercicio).get(id_ejercicios_muestra[i])
            rutina3.ejercicios.append(ejercicio)
            db.session.commit()

        #Definir endpoint, encabezados y hacer el llamado
        endpoint_rutinasEntrenamiento = "/rutinasEntrenamiento" 
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_rutinasEntrenamiento = self.client.get(endpoint_rutinasEntrenamiento,
                                                         headers=headers)

               
        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta_rutinasEntrenamiento = json.loads(resultado_rutinasEntrenamiento.get_data())

        #Verificar que el llamado fue exitoso
        self.assertEqual(resultado_rutinasEntrenamiento.status_code, 200)
        
        #Obtener los id's de las rutinas de la respuesta
        id_rutinasEntrenamiento = []
        for i in range(len(datos_respuesta_rutinasEntrenamiento)):
            id_rutina = datos_respuesta_rutinasEntrenamiento[i]['id']
            id_rutinasEntrenamiento.append(id_rutina)
        
        #Verificar que rutina1 tiene menos de 3 ejercicios (no pertenece a la respuesta)
        self.assertNotIn('1', id_rutinasEntrenamiento)

        #Verificar que rutina2 tiene 3 ejercicios o mas (pertenece a la respuesta)
        self.assertIn('2', id_rutinasEntrenamiento)

        #Verificar que rutina3 tiene 3 ejercicios o mas (pertenece a la respuesta)
        self.assertIn('3', id_rutinasEntrenamiento)


if __name__ == '__main__':
    unittest.main()
