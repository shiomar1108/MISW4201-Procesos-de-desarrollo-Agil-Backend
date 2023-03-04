import json
import hashlib
from faker import Faker
import unittest
from modelos import db, Usuario, Rutina, Ejercicio, Entrenamiento
from app import app
import random
from datetime import datetime, timedelta

class TestReporteIMC(unittest.TestCase):

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
        
        
    # def tearDown(self):
    #     entrenamientos = db.session.query(Entrenamiento).all()
    #     for entrenamiento in entrenamientos:
    #         db.session.delete(entrenamiento)
    #         db.session.commit()
    #     rutinas = db.session.query(Rutina).all()
    #     for rutina in rutinas:
    #         db.session.delete(rutina)
    #         db.session.commit()
    #     ejercicios = db.session.query(Ejercicio).all()
    #     for ejercicio in ejercicios:
    #         db.session.delete(ejercicio)
    #         db.session.commit() 
    #     usuarios = db.session.query(Usuario).all()           
    #     for usuario in usuarios:
    #         db.session.delete(usuario)
    #         db.session.commit()



    def test_resultados_entrenamientos(self):
        #Crear los datos de la rutina 
        self.data_factory = Faker()
        Faker.seed(1000)              
        rutina1 = Rutina(nombre=self.data_factory.first_name(), descripcion=self.data_factory.sentence())        
        db.session.add(rutina1)        
        db.session.commit()           
        
        #Crear tres ejercicios y asociarlos a rutina1
        self.data = []
        self.ejercicio = []
        for i in range(0, 3):
            self.data.append((
                self.data_factory.first_name(),
                self.data_factory.sentence(),
                self.data_factory.file_path(depth=3),
                self.data_factory.random_int(5, 15)
            ))
            self.ejercicio.append(
                Ejercicio(
                    nombre=self.data[-1][0],
                    descripcion=self.data[-1][1],
                    video=self.data[-1][2],
                    calorias=self.data[-1][3]
                ))
            db.session.add(self.ejercicio[-1])
            rutina1.ejercicios.append(self.ejercicio[-1])
            db.session.commit()
        
        #Crear Entrenamiento para ejercicios de rutina1
        for i in range(len(rutina1.ejercicios)):
            entrenamientoRutina = Entrenamiento(fecha=datetime.now(), persona=self.usuario_id, ejercicio=rutina1.ejercicios[i].id, repeticiones=random.randint(5,10))
            db.session.add(entrenamientoRutina)
            db.session.commit()            
            #Asociar rutina a entrenamiento1
            rutina1.entrenamientos.append(entrenamientoRutina)
            db.session.commit()


        #Crear Entrenamiento para ejercicios
        ejercicios = db.session.query(Ejercicio).all()        
        for i in range(len(ejercicios)):
            entrenamientoEjercicio = Entrenamiento(fecha=datetime.now()+timedelta(days=1), persona=self.usuario_id, repeticiones=random.randint(5,10))
            db.session.add(entrenamientoEjercicio)
            db.session.commit()
            #Asociar ejercicio a entrenamiento
            ejercicios[i].entrenamientos.append(entrenamientoEjercicio)
            db.session.commit()
          
       

        #Definir endpoint, encabezados y hacer el llamado
        endpoint_resultadosEntrenamientos = "/resultadosEntrenamientos" 
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_resultadosEntrenamientos = self.client.get(endpoint_resultadosEntrenamientos,
                                                         headers=headers)

               

        #Verificar que el llamado fue exitoso
        self.assertEqual(resultado_resultadosEntrenamientos.status_code, 200)


        



        

       



