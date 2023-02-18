from faker import Faker
import unittest
from modelos import db, Rutina, Ejercicio
from app import app

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



if __name__ == '__main__':
    unittest.main()
