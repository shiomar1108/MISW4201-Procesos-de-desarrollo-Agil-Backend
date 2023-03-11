from flask import request, jsonify
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from .utilidad_reporte import UtilidadReporte
import hashlib
from json import dumps
from itertools import groupby
import re

from modelos import \
    db, \
    Ejercicio, EjercicioSchema, rutinas_ejercicios, \
    Persona, PersonaSchema, \
    Entrenamiento, EntrenamientoSchema, \
    Usuario, UsuarioSchema, \
    Rutina, RutinaSchema, \
    ReporteGeneralSchema, ReporteDetalladoSchema


ejercicio_schema = EjercicioSchema()
persona_schema = PersonaSchema()
entrenamiento_schema = EntrenamientoSchema()
usuario_schema = UsuarioSchema()
rutina_schema = RutinaSchema()
reporte_general_schema = ReporteGeneralSchema()
reporte_detallado_schema = ReporteDetalladoSchema()

class VistaSignIn(Resource):

    def post(self):
        pattern = re.compile("(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z0-9].{7,}")
        contrasena_val =  request.json["contrasena"]
        if pattern.match(contrasena_val) :
            usuario = Usuario.query.filter(
                Usuario.usuario == request.json["usuario"]).first()
            if usuario is None:
                contrasena_encriptada = hashlib.md5(
                    request.json["contrasena"].encode('utf-8')).hexdigest()
                if not "rol" in request.json:
                    nuevo_usuario = Usuario(
                        usuario=request.json["usuario"], contrasena=contrasena_encriptada, rol="ENT")
                else:
                    nuevo_usuario = Usuario(
                        usuario=request.json["usuario"], contrasena=contrasena_encriptada, rol=request.json["rol"])
                db.session.add(nuevo_usuario)
                db.session.commit()

                # Creacion de entrenador
                if nuevo_usuario.rol == "ENT":
                    nueva_persona = Persona(
                        nombre=request.json["nombre"],
                        apellido=request.json["apellido"],
                        usuario=nuevo_usuario.id,
                        entrenando=False
                    )
                    db.session.add(nueva_persona)
                    db.session.commit()

                return {"mensaje": "usuario creado exitosamente", "id": nuevo_usuario.id}
            else:
                return "El usuario ya existe", 409
        else:
            return "Contrasena invalida", 409

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.contrasena = request.json.get("contrasena", usuario.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204

    def get(self):
        return "prueba3", 200


class VistaLogIn(Resource):

    def post(self):
        contrasena_encriptada = hashlib.md5(
            request.json["contrasena"].encode('utf-8')).hexdigest()
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"],
                                       Usuario.contrasena == contrasena_encriptada).first()
        rol = usuario.rol
        db.session.commit()
        if usuario is None:
            return "El usuario no existe", 404
        else:
            token_de_acceso = create_access_token(identity=usuario.id)
            rol = usuario.rol
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso, "id": usuario.id, "rol": rol}


class VistaPersonas(Resource):
    @jwt_required()
    def get(self, id_usuario):
        personas = Persona.query.filter(Persona.entrenador == id_usuario)
        return [persona_schema.dump(persona) for persona in personas]

    @jwt_required()
    def post(self, id_usuario):
        if "usuario" and "contrasena" in request.json:
            usuarioACrear = request.json["usuario"]
            usuario = Usuario.query.filter(Usuario.usuario == usuarioACrear).first()
            # Validamos si el usuario ya esta registrado
            if usuario is None:
                # Creación del usuario
                contrasena_encriptada = hashlib.md5(
                    request.json["contrasena"].encode('utf-8')).hexdigest()
                nuevo_usuario = Usuario(
                        usuario=usuarioACrear, contrasena=contrasena_encriptada, rol="CLI")
                db.session.add(nuevo_usuario)
                db.session.commit()
            else:
                return "El usuario ya existe", 409
        # Creación del cliente
        nueva_persona = Persona(
            nombre=request.json["nombre"],
            apellido=request.json["apellido"],
            talla=float(request.json["talla"]),
            peso=float(request.json["peso"]),
            edad=float(request.json["edad"]),
            ingreso=datetime.strptime(request.json["ingreso"], '%Y-%m-%d'),
            brazo=float(request.json["brazo"]),
            pecho=float(request.json["pecho"]),
            cintura=float(request.json["cintura"]),
            pierna=float(request.json["pierna"]),
            entrenando=bool(request.json["entrenando"]),
            razon=request.json["razon"],
            terminado=datetime.strptime(request.json["terminado"], '%Y-%m-%d'),
            entrenador=id_usuario
        )
        db.session.add(nueva_persona)
        db.session.commit()
        return persona_schema.dump(nueva_persona)
        

class VistaPersona(Resource):
    @jwt_required()
    def get(self, id_persona):
        return persona_schema.dump(Persona.query.get_or_404(id_persona))

    @jwt_required()
    def put(self, id_persona):
        persona = Persona.query.get_or_404(id_persona)
        persona.nombre = request.json["nombre"]
        persona.apellido = request.json["apellido"]
        persona.talla = float(request.json["talla"])
        persona.peso = float(request.json["peso"])
        persona.edad = float(request.json["edad"])
        persona.ingreso = datetime.strptime(
            request.json["ingreso"], '%Y-%m-%d')
        persona.brazo = float(request.json["brazo"])
        persona.pecho = float(request.json["pecho"])
        persona.cintura = float(request.json["cintura"])
        persona.pierna = float(request.json["pierna"])
        persona.entrenando = bool(request.json["entrenando"])
        persona.razon = request.json["razon"]
        persona.terminado = datetime.strptime(
            request.json["terminado"], '%Y-%m-%d')
        db.session.commit()
        return persona_schema.dump(persona)

    @jwt_required()
    def delete(self, id_persona):
        persona = Persona.query.get_or_404(id_persona)
        if not persona.entrenamientos:
            db.session.delete(persona)
            db.session.commit()
            return '', 204
        else:
            return 'La persona tiene entrenamientos asociados', 409


class VistaEjercicios(Resource):
    @jwt_required()
    def get(self):
        ejercicios = Ejercicio.query.all()
        return [ejercicio_schema.dump(ejercicio) for ejercicio in ejercicios]

    @jwt_required()
    def post(self):
        nuevo_ejercicio = Ejercicio(
            nombre=request.json["nombre"],
            descripcion=request.json["descripcion"],
            video=request.json["video"],
            calorias=float(request.json["calorias"]),
        )
        db.session.add(nuevo_ejercicio)
        db.session.commit()
        return ejercicio_schema.dump(nuevo_ejercicio)


class VistaEjercicio(Resource):
    @jwt_required()
    def get(self, id_ejercicio):
        return ejercicio_schema.dump(Ejercicio.query.get_or_404(id_ejercicio))

    @jwt_required()
    def put(self, id_ejercicio):
        ejercicio = Ejercicio.query.get_or_404(id_ejercicio)
        ejercicio.nombre = request.json["nombre"]
        ejercicio.descripcion = request.json["descripcion"]
        ejercicio.video = request.json["video"]
        ejercicio.calorias = float(request.json["calorias"])
        db.session.commit()
        return ejercicio_schema.dump(ejercicio)

    @jwt_required()
    def delete(self, id_ejercicio):
        ejercicio = Ejercicio.query.get_or_404(id_ejercicio)
        #if not ejercicio.entrenamientos:
        db.session.delete(ejercicio)
        db.session.commit()
        return '', 204
        #else:
            #return 'El ejercicio tiene entrenamientos asociados', 409


class VistaEntrenamientos(Resource):
    @jwt_required()
    def get(self, id_persona):
        persona = Persona.query.get_or_404(id_persona)
        entrenamiento_array = []
        for entrenamiento in persona.entrenamientos:
            ejercicio = Ejercicio.query.get_or_404(entrenamiento.ejercicio)
            entrenamiento_schema_dump = entrenamiento_schema.dump(entrenamiento)
            if entrenamiento_schema_dump['rutina'] == None:
              entrenamiento_schema_dump['ejercicio'] = ejercicio_schema.dump(ejercicio)
              entrenamiento_array.append(entrenamiento_schema_dump)
        return [entrenamiento for entrenamiento in entrenamiento_array]

    @jwt_required()
    def post(self, id_persona):
        nuevo_entrenamiento = Entrenamiento(
            tiempo=datetime.strptime(
                request.json["tiempo"], '%H:%M:%S').time(),
            repeticiones=float(request.json["repeticiones"]),
            fecha=datetime.strptime(request.json["fecha"], '%Y-%m-%d').date(),
            ejercicio=request.json["ejercicio"],
            persona=id_persona
        )
        db.session.add(nuevo_entrenamiento)
        db.session.commit()
        return ejercicio_schema.dump(nuevo_entrenamiento)


class VistaEntrenamiento(Resource):
    @jwt_required()
    def get(self, id_entrenamiento):
        return entrenamiento_schema.dump(Entrenamiento.query.get_or_404(id_entrenamiento))

    @jwt_required()
    def put(self, id_entrenamiento):
        entrenamiento = Entrenamiento.query.get_or_404(id_entrenamiento)
        entrenamiento.tiempo = datetime.strptime(
            request.json["tiempo"], '%H:%M:%S').time()
        entrenamiento.repeticiones = float(request.json["repeticiones"])
        entrenamiento.fecha = datetime.strptime(
            request.json["fecha"], '%Y-%m-%d').date()
        entrenamiento.ejercicio = request.json["ejercicio"]
        entrenamiento.persona = request.json["persona"]
        db.session.commit()
        return entrenamiento_schema.dump(entrenamiento)

    @jwt_required()
    def delete(self, id_entrenamiento):
        entrenamiento = Entrenamiento.query.get_or_404(id_entrenamiento)
        db.session.delete(entrenamiento)
        db.session.commit()
        return '', 204


class VistaReporte(Resource):

    @jwt_required()
    def get(self, id_persona):
        reporte = []
        reporte_entrenamiento = []
        utilidad = UtilidadReporte()
        data_persona = Persona.query.get_or_404(id_persona)
        imc_calculado = utilidad.calcular_imc(
            data_persona.talla, data_persona.peso)
        clasificacion_imc_calculado = utilidad.dar_clasificacion_imc(
            imc_calculado)

        reporte_persona = dict(persona=data_persona, imc=imc_calculado,
                               clasificacion_imc=clasificacion_imc_calculado)
        reporte_persona_schema = reporte_general_schema.dump(reporte_persona)

        for entrenamiento in data_persona.entrenamientos:
            data_entrenamiento = dict(
                fecha=entrenamiento.fecha, repeticiones=entrenamiento.repeticiones, calorias=1)
            reporte_entrenamiento.append(
                reporte_detallado_schema.dump(data_entrenamiento))

        reporte_persona_schema['resultados'] = utilidad.dar_resultados(
            data_persona.entrenamientos)

        return reporte_persona_schema


class VistaEntrenadores(Resource):
    @jwt_required()
    def get(self):
        entrenadores = [usuario_schema.dump(
            usuario) for usuario in Usuario.query.filter_by(rol="ENT").all()]
        entrenadores_list = [val['id'] for val in entrenadores]
        return [persona_schema.dump(persona) for persona in Persona.query.filter(Persona.usuario.in_(entrenadores_list)).all()]


class VistaEntrenador(Resource):
    @jwt_required()
    def delete(self, id_usuario):
        personas = Persona.query.filter_by(entrenador=id_usuario).all()
        if len(personas) == 0:
             # Se elimina la persona
            persona = Persona.query.filter_by(usuario=id_usuario).first()
            db.session.delete(persona)
            db.session.commit()
            # Se elimina el usuario
            usuario = Usuario.query.get_or_404(id_usuario)
            db.session.delete(usuario)
            db.session.commit()
            return '', 204
        else:
            return 'El entrenador tienen clientes asociados', 409


class VistaRutinas(Resource):
    @jwt_required()
    def get(self):
        rutinas = Rutina.query.all()
        return [rutina_schema.dump(rutina) for rutina in rutinas]
        

    @jwt_required()
    def post(self):
        rutinas_creadas = Rutina.query.all()
        nueva_rutina = Rutina(
            nombre=request.json["nombre"],
            descripcion=request.json["descripcion"],
        )
        for rutina in rutinas_creadas:
            if rutina.nombre.lower() == nueva_rutina.nombre.lower():
                return "La Rutina ya existe", 409 
        db.session.add(nueva_rutina)
        db.session.commit()
        return rutina_schema.dump(nueva_rutina)
            
        
        
    
class VistaRutina(Resource):
    @jwt_required()
    def get(self, id_rutina):        
        return rutina_schema.dump(Rutina.query.get_or_404(id_rutina))

class VistaRutinaDiferente(Resource):
    @jwt_required()
    def get(self, id_rutina):
        ejerciciosDisponibles = []
        ejerciciosRutina = rutina_schema.dump(Rutina.query.get_or_404(id_rutina))
        ejerciciosRutinaString = dumps(ejerciciosRutina)
        ejercicios = Ejercicio.query.all()
        lista_ejercicios = [ejercicio_schema.dump(ejercicio) for ejercicio in ejercicios]
        for ejercicio in lista_ejercicios:
            nombreEjercicio = ejercicio['nombre']
            if not nombreEjercicio in ejerciciosRutinaString:
              ejerciciosDisponibles.append(ejercicio)
        return ejerciciosDisponibles       

 
class VistaRutinaEjercicio(Resource):    
    @jwt_required()
    def put(self, id_rutina, id_ejercicio):        
        rutina = db.session.query(Rutina).get_or_404(id_rutina)
        ejercicio = db.session.query(Ejercicio).get_or_404(id_ejercicio)        
        rutina.ejercicios.append(ejercicio)
        db.session.commit()
        return  rutina_schema.dump(rutina)

class VistaRutinasEntrenamiento(Resource):    
    @jwt_required()
    def get(self):        
        sql_rutinas = db.session.execute('SELECT Q1.ID FROM RUTINA AS Q1, (SELECT RUTINA_ID, COUNT(RUTINA_ID) AS TOTAL_EJERCICIOS FROM RUTINA_EJERCICIO GROUP BY RUTINA_ID) \
                                          AS Q2 WHERE Q1.ID=Q2.RUTINA_ID AND Q2.TOTAL_EJERCICIOS>=3')                 
              
        id_rutinas = sql_rutinas.scalars().all()  
        rutinas = db.session.query(Rutina).all()
        rutinasEntrenamiento = []
        for rutina in rutinas:
            if rutina.id in id_rutinas:
                rutinasEntrenamiento.append(rutina)

        return [rutina_schema.dump(rutina) for rutina in rutinasEntrenamiento]
    

    @jwt_required()
    def post(self):
        idRutina = request.json["idRutina"]
        fecha = datetime.strptime(request.json["fecha"], '%Y-%m-%d').date()
        idPersona = request.json["idPersona"]
        entrenamientos = request.json["entrenamientos"]
        
        for entrenamiento in entrenamientos:
            repeticiones = entrenamiento['repeticiones']            
            nuevo_entrenamiento = Entrenamiento(
                tiempo=datetime.strptime(
                    entrenamiento["tiempo"], '%H:%M:%S').time(),
                repeticiones=entrenamiento["repeticiones"], 
                fecha=fecha,
                ejercicio=entrenamiento["ejercicio"],
                persona=idPersona,
                rutina=idRutina                
            )
            db.session.add(nuevo_entrenamiento)
            db.session.commit()
        
        data =  "Se realiza la creación exitosa"
        # Creating a dictionary
        response = {"mensaje": "proceso exitoso"}
        return response, 200



class VistaRutinaEntrenamientoPersona(Resource):
    @jwt_required()
    def get(self,id_persona):
        persona = Persona.query.get_or_404(id_persona)
        entrenamientorutina_array = []
        for entrenamiento in persona.entrenamientos:
            ejercicio = Ejercicio.query.get_or_404(entrenamiento.ejercicio)
            entrenamiento_schema_dump = entrenamiento_schema.dump(entrenamiento)
            if entrenamiento_schema_dump['rutina'] != None:
              entrenamiento_schema_dump['ejercicio'] = ejercicio_schema.dump(ejercicio)
              entrenamientorutina_array.append(entrenamiento_schema_dump)
        
        result = []
        key_function = lambda x: (x["fecha"], x["rutina"], x["persona"])
        entrenamientorutina_array.sort(key = key_function)
        for group, entrenamientos in groupby(entrenamientorutina_array, key_function):
                user = {
                        "fecha": group[0],
                        "rutina": rutina_schema.dump(Rutina.query.get_or_404(group[1])),
                        "persona": group[2],
                        "repeticionesTotales": 0,
                        "tiempoTotal": "00:00:00",
                        "entrenamientos": []
                }
                ttoal = [0,0,0]
                for entrenamiento in entrenamientos:
                    user["repeticionesTotales"] += int(float(entrenamiento["repeticiones"]))
                    arr = entrenamiento["tiempo"].split(':')
                    ttoal[0] += int(arr[0])
                    ttoal[1] += int(arr[1])
                    if(ttoal[1] > 60):
                        ttoal[0] += int(ttoal[1] / 60)
                        ttoal[1] = int(ttoal[1] % 60)
                    ttoal[2] += int(arr[2])
                    if(ttoal[2] > 60):
                        ttoal[1] += int(ttoal[2] / 60)
                        ttoal[2] = int(ttoal[2] % 60)
                    user["entrenamientos"].append(entrenamiento)
                user["tiempoTotal"] = str(datetime.strptime(":".join(str(n) for n in ttoal), '%H:%M:%S').time())
                result.append(user)
        return [entrenamientoRutina for entrenamientoRutina in result]
   


class VistaResultadosEntrenamientos(Resource):
    @jwt_required()
    def get(self, id_persona):
        sql_resultados = db.session.execute("SELECT T1.persona, T1.fecha, T1.[Tipo de Entrenamiento], SUM(repeticiones) AS [Repeticiones Ejecutadas], SUM(T1.[Total Calorias]) AS [Calorias Consumidas] \
                                            FROM (SELECT ENTR.persona, ENTR.fecha, 'Ejercicio' AS [Tipo de Entrenamiento], ENTR.repeticiones, EJER.calorias AS calorias_por_repeticion, ENTR.repeticiones*EJER.calorias AS [Total Calorias] \
                                            FROM ENTRENAMIENTO AS ENTR, EJERCICIO AS EJER WHERE ENTR.RUTINA IS NULL AND ENTR.EJERCICIO=EJER.ID) AS T1 GROUP BY T1.Fecha, T1.[Tipo de Entrenamiento] HAVING persona="+str(id_persona)+" " \
                                            "UNION SELECT T1.persona, T1.fecha, T1.[Tipo de Entrenamiento], SUM(repeticiones) AS [Repeticiones Ejecutadas], SUM(T1.[Total Calorias]) AS [Calorias Consumidas] \
                                            FROM (SELECT ENTR.persona, ENTR.fecha, 'Rutina' AS [Tipo de Entrenamiento], ENTR.repeticiones, EJER.calorias AS calorias_por_repeticion, ENTR.repeticiones*EJER.calorias AS [Total Calorias] \
                                            FROM ENTRENAMIENTO AS ENTR, EJERCICIO AS EJER WHERE ENTR.RUTINA IS NOT NULL AND ENTR.EJERCICIO=EJER.ID) AS T1 GROUP BY T1.Fecha, T1.[Tipo de Entrenamiento] HAVING persona="+str(id_persona)+" ORDER BY fecha, [Tipo de Entrenamiento]")
        
        
        return jsonify([dict(registro) for registro in sql_resultados])
    
