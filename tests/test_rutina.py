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
        contrasena = 'T1$' + self.data_factory.word()
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
            #print('ejercicios............................')
            db.session.add(ejercicio[-1])
            db.session.commit()


        ejercicios = db.session.query(Ejercicio).all()
        for i in range(0, len(ejercicios)):
            #print('ejercicios............................')
            print(ejercicios[i])
            rutina.ejercicios.append(ejercicios[i])
            db.session.commit()

        
        #COnsultar Ejercicios de una Rutina por Servicio
        endpoint_rutinas = "/rutina/" + str(rutina.id)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_consulta_rutina = self.client.get(endpoint_rutinas,                                                  
                                                   headers=headers)

        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta_rutina = json.loads(resultado_consulta_rutina.get_data())
        #print('resutado =======')
        #print(datos_respuesta_rutina)        
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



if __name__ == '__main__':
    unittest.main()
