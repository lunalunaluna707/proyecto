from flask import Flask
import os
import base64
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from flask import jsonify
from empleadoF import empleadoFacade
from datetime import datetime,  timedelta

import pusher
import mysql.connector
from handlers import pusherHandler, consultaHandler, pusherHandlerID, eliminarHandler, BDHandler
import pytz
from pusher_manager import PusherManager
import pusher


app = Flask(__name__) 

utc_now = datetime.now(pytz.utc)
adjusted_time = utc_now - timedelta(minutes=10)  
print("Hora ajustada en UTC:", adjusted_time)

pusher_client = pusher.Pusher(
app_id='1864238',
key='2ea386b7b90472052932',
secret='578df1dc2b254c75c850',
cluster='us2',
ssl=True
)

host = "185.232.14.52"
database = "u760464709_vzqzluna_bd"
user = "u760464709_vzqzluna_usr"
password = "g4iqen$H"




empleado_facade = empleadoFacade(host, database, user, password)


class Conexion:
    @staticmethod
    def create_connection(db_type='mysql'):
        if db_type=='mysql':
            return connBD()
        else:
            raise ValueError("Tipo de base de datos no soportado")
class connBD:
    def __init__(self):
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host="185.232.14.52",
                database="u760464709_vzqzluna_bd",  
                user="u760464709_vzqzluna_usr",
                password="g4iqen$H"
            )
            if self.connection.is_connected():
                print("Conexión a la base de datos MySQL exitosa.")
            return self.connection
        except mysql.connector.Error as err:
            print("Error al conectar con MySQL:", err)
            return None

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión a la base de datos cerrada.")

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except mysql.connector.Error as err:
            print("Error al ejecutar la consulta:", err)
            self.connection.rollback()
            return None
        finally:
            cursor.close()

class consultaMaquina:
    def __init__(self):
        self.db= Conexion.create_connection('mysql')
        self.con=self.db.connect()
    def maquinas(self):
        registros = []
        try:
            if self.con:
                cursor = self.con.cursor()
                cursor.execute("SELECT * FROM maquinas")  
                registros = cursor.fetchall()
                registros = [
                    {
                        "Id_Maquina": row[0],
                        "Nombre": row[1],
                        "Placas": row[2],
                        "Linea": row[3],
                        "Marca": row[4],
                        "Modelo": row[5],
                        "Serie": row[6],
                        "Imagen": row[7]
                    }
                    for row in registros
                ]

                print("Registros de máquinas obtenidos:", registros)
        except mysql.connector.Error as err:
            print("Error al conectar con MySQL:", err)
            registros = []  
        finally:
            if self.con and self.con.is_connected():
                cursor.close()
                self.db.close()
        
        return registros


class InsertarNuevaMaquina:
    def __init__(self, con_db):
        self.con_db= con_db
    def insertar(self, nombre, placa, modelo, linea, marca, serie, imagen_path):
        sql="""INSERT INTO maquinas(Nombre, Placas, Modelo, Linea, Marca, Serie, Imagen)
        VALUES (%s, %s, %s, %s, %s, %s,%s)"""
        parametros=(nombre, placa, modelo, linea, marca, serie, imagen_path)
        cursor= self.con_db.execute_query(sql,parametros)
        if cursor:
            print(f"MAQUINA REGISTRADA EXITOSAMENTE: {nombre} ")
            return True
        return False
    
class MaquinaEliminar:
    def __init__(self, con_db):
        self.con_db= con_db
    def eliminar(self, id_maquina):
        sql="DELETE FROM maquinas WHERE Id_Maquina= %s"
        parametro=(id_maquina,)
        cursor= self.con_db.execute_query(sql,parametro)
        if cursor:
            print(f"MAQUINA ELIMINA EXITOSAMENTE: {id_maquina} ")
            return True
        return False
class MaquinaActualizar:
    def __init__(self, con_db):
        self.con_db = con_db
    
    def actualizar(self, id_maquina, nombre, placa, modelo, linea, marca, serie, imagen_path=None):
        sql = """
            UPDATE maquinas 
            SET Nombre = %s, Placas = %s, Modelo = %s, Linea = %s, Marca = %s, Serie = %s
        """
        parametros = (nombre, placa, modelo, linea, marca, serie)

        if imagen_path:
            sql += ", Imagen = %s"
            parametros += (imagen_path,)

        sql += " WHERE Id_Maquina = %s"
        parametros += (id_maquina,)

        cursor = self.con_db.execute_query(sql, parametros)
        if cursor:
            print(f"Máquina con ID {id_maquina} actualizada exitosamente.")
            return True
        return False

        
@app.route('/obtener_mantenimientos/<int:id>', methods=['GET'])
def obtener_mantenimientos(id):
    db = Conexion.create_connection('mysql')
    con = db.connect()
    mantenimientos = []
    try:
        if not con or not con.is_connected():
            return jsonify({"error": "No se puede conectar a la base de datos"}), 500
        cursor = con.cursor(dictionary=True) 
        sql_mantenimiento = "SELECT * FROM mantenimiento_realizada WHERE Id_Maquina = %s"
        cursor.execute(sql_mantenimiento, (id,))
        mantenimientos = cursor.fetchall()  

        if not mantenimientos:
            return jsonify({"message": "No se encontraron mantenimientos para esta máquina"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": "Error al conectar con MySQL", "details": str(err)}), 500

    finally:
        if con and con.is_connected():
            cursor.close()
            con.close()
    return jsonify({"mantenimientos": mantenimientos})



@app.route('/maquinas', methods=['GET'])
def maquinas():
    registros = []
    db=Conexion.create_connection('mysql')
    con=db.connect()
    try:
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM maquinas")  
            registros = cursor.fetchall()
            print("Registros de máquinas obtenidos:", registros)
    except mysql.connector.Error as err:
        print("Error al conectar con MySQL:", err)
        registros = []  
    finally:
        if con and con.is_connected():
            cursor.close()
       
            db.close()
    
    return render_template('maquinas.html', registros=registros)  

@app.route('/vistamaquina')
def vistamaquina():
    consulta= consultaMaquina()
    registros=consulta.maquinas()
    for registro in registros:
        if registro['Imagen']:
            registro['Imagen'] = f'{registro["Imagen"]}' 
    return jsonify(registros)

@app.route("/listamaquina")
def indexmaquina():
    db=Conexion.create_connection('mysql')
    con=db.connect()
    try:
        if not con:
            return "No se pudo conectar. Verifique su conexion", 500
    except mysql.connector.Error as err:
        print("Error al conectar:", err)
        return "No se pudo conectar. Verifique su conexion", 500
    finally:
        if con and con.is_connected():
            con.close()
    return render_template("maquinas.html")



@app.route('/calcular')
def calcular_formulario():
    try:
        connection = mysql.connector.connect(
                host = "185.232.14.52",
                database = "u760464709_vzqzluna_bd",
                user = "u760464709_vzqzluna_usr",
                password = "g4iqen$H"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT Id_Maquina, Nombre FROM maquinas")
        maquinas = cursor.fetchall()

        return render_template('mantenimiento-calculo.html', maquinas=maquinas)
    except Exception as e:
        print(f"Error: {str(e)}")
        return "Error al cargar las máquinas"
    finally:
        if 'connection' in locals():
            connection.close()



@app.route('/formmaquina')
def formulariomaquina():
    return render_template('form-maquina.html')


@app.route('/editarmaquina/<int:id>', methods=['GET','POST'])
def editarmaquina(id, message=None):
    con= None
    registros=[]

    try:
        con = mysql.connector.connect(
                host = "185.232.14.52",
                database = "u760464709_vzqzluna_bd",
                user = "u760464709_vzqzluna_usr",
                password = "g4iqen$H"
        )
        if not con.is_connected():
            raise msql.connector.Error('No se pudo conectar a la base de datos')
        
        cursor = con.cursor()
        sql= "SELECT * FROM maquinas WHERE Id_Maquina= %s"
        cursor.execute(sql,(id,))
        registros = cursor.fetchall()
        if len(registros)==0:
            message="No se encontro registro con este ID"
            return render_template('editar-maquina.html', message=message, registros=[])
        print("Registros obtenidos:", registros)
    except mysql.connector.Error as err:
        print("Error al conectar con MySQL:", err)
        registros = []  
        message="No se pudo conectar. Verificar conexión."
    finally:
        if con and con.is_connected():
            cursor.close()
            con.close()
    
    return render_template('editar-maquina.html', registros=registros, message=message)

@app.route('/actualizarmaquina/<int:id>', methods=['POST'])
def actualizarmaquina(id):
    db = connBD()  
    con = db.connect()
    if con:
        actualizar = MaquinaActualizar(db)  
        nombre = request.form['txtnombremaquina']
        placa = request.form['txtplaca']
        modelo = request.form['txtmodelo']
        linea = request.form['txtlinea']
        marca = request.form['txtmarca']
        serie = request.form['txtserie']
        
        imagen_path = None

        if 'imagen' in request.files and request.files['imagen'].filename != '':
            imagen = request.files['imagen']
            imagen_filename = imagen.filename
            imagen_path = os.path.join('static', 'imagenes', imagen_filename)

            try:
                imagen.save(imagen_path)
            except Exception as e:
                return render_template('form-maquina.html', message=f"Error al guardar imagen: {str(e)}")

        if actualizar.actualizar(id, nombre, placa, modelo, linea, marca, serie, imagen_path):
            message = "¡Máquina actualizada exitosamente!"
            pusher_manager = PusherManager()
            evento_data = {
                'message': f'Máquina actualizada: {nombre}, {placa}, {modelo}, {linea}, {marca}, {serie}'
            }
            pusher_manager.enviar_evento('my-channel', 'my-event', evento_data)
        else:
            message = "Error al actualizar la máquina."
        db.close()
        return redirect(url_for('editarmaquina', id=id, message=message))
    else:
        return "No se pudo conectar a la base de datos.", 500



@app.route('/formempleado')
def formularioempleado():
    return render_template('form-empleados.html')
@app.route('/eventomaquina', methods=["GET", "POST"])
def eventomaquina():
    message = ""
    if request.method == 'POST':
        nombremaquina = request.form.get('txtnombremaquina')
        placa = request.form.get('txtplaca')
        modelo = request.form.get('txtmodelo')
        marca = request.form.get('txtmarca')
        serie = request.form.get('txtserie')
        linea = request.form.get('txtlinea')

        if 'imagen' not in request.files or request.files['imagen'].filename == '':
            return render_template('form-maquina.html', message="Debe subir una imagen.")
        
        imagen = request.files['imagen']
        imagen_filename = imagen.filename
        imagen_path = os.path.join('static', 'imagenes', imagen_filename)

        try:
            imagen.save(imagen_path)
        except Exception as e:
            return render_template('form-maquina.html', message=f"Error al guardar imagen: {str(e)}")

        db = Conexion.create_connection('mysql')
        con = db.connect()
        if con:
            accion = InsertarNuevaMaquina(db)
            if accion.insertar(nombremaquina, placa, modelo, linea, marca, serie, imagen_path):
                message = '¡SE REGISTRÓ EXITOSAMENTE!'
 
                pusher_manager = PusherManager()
                pusher_manager.enviar_evento('my-channel', 'my-event', {
                    'message': f'Nuevo evento: {nombremaquina}, {placa}, {modelo}, {linea}, {marca}, {serie}'
                })
            else:
                message = "Error al registrar máquina"
            db.close()
        return render_template('form-maquina.html', message=message)
    return render_template('form-maquina.html')

@app.route('/apartadomaquina')
def apartado_maquina():
    return render_template('apartado_maquina.html')

@app.route('/maquina/<int:id>', methods=['GET','POST'])
def mostrarmaquina(id, message=None):
    db=Conexion.create_connection('mysql')
    con=db.connect()
    registros={}
    mantenimientos = []
    operador=None
    try:
        if not con or not con.is_connected():
            message="No se puede conectar a la base de datos"
            return render_template('apartado_maquina.html', message=message, registros={}, mantenimientos=[], operador=None) 
        
        cursor = con.cursor()

        sql= "SELECT * FROM maquinas WHERE Id_Maquina= %s"
        cursor.execute(sql,(id,))
        registros = cursor.fetchone()

        sql_mantenimiento= "SELECT * FROM mantenimiento_realizada WHERE Id_Maquina= %s"
        cursor.execute(sql_mantenimiento,(id,))
        mantenimientos = cursor.fetchall()

        if registros:
            sql_operador="""SELECT e.Nombre_Empleado FROM empleados e JOIN asignar_maquina a 
            ON e.Id_Empleado =a.Id_Empleado  WHERE a.Id_Maquina= %s"""
            cursor.execute(sql_operador,(id,))
            operador = cursor.fetchone()
            print("Operador obtenido:", operador)

        if registros is None:
            message="No se encontro registro con este ID"
            return render_template('apartado_maquina.html', message=message, registros={}, mantenimientos=[], operador=None)

        print("Registros obtenidos:", registros)
    except mysql.connector.Error as err:
        print("Error al conectar con MySQL:", err)
        registros = {}
        mantenimientos=[]
        operador=None

        message="No se pudo conectar. Verificar conexión."
    finally:
        if con and con.is_connected():
            cursor.close()
            db.close()
    
    return render_template('apartado_maquina.html', registros=registros, mantenimientos=mantenimientos, operador=operador, message=message)





@app.route('/empleados', methods=['GET'])
def empleados():
    registros = empleado_facade.obtener_empleados()
    return render_template('empleados.html', registros=registros)  

@app.route('/eventoempleado', methods=["GET","POST"])
def eventoempleado():
    message=''
    if request.method=='POST':
        empleados=(
            request.form['txtnombre'],
            request.form['txtnumempleado'],
            request.form['txttel'],
            request.form['txtdomicilio'],
            request.form['txtcurp'],
            request.form['txtnss'],
            request.form['txtrfc'],
            request.form['txtcorreo']
        )
        resultado=empleado_facade.agregar_empleado(empleados)
        if resultado>0:
            message='SE REGISTRO CORRECTAMENTE'
            pusher_client.trigger('my-channel', 'my-event', {'message': f'Nuevo empleado agregado: {empleados[0]}'})
        else:
            message = 'Error al enviar encuesta'
    return render_template('form-empleados.html', message=message)



@app.route('/eliminarmaquina/<int:id>', methods=['POST'])
def eliminarmaquina(id):
    db=Conexion.create_connection('mysql')
    con=db.connect()

    if con:
        accion=MaquinaEliminar(db)
        if accion.eliminar(id):
            message = f'¡SE ELIMINO CORRECTAMENTE EL ID {id}!'
            pusher_client.trigger('my-channel', 'my-event', {'message': f'Nuevo evento: {id}'})
        else: 
            message=f'ERROR AL ELIMINAR EL ID {id}'
            db.close
    return jsonify({"message": message})

@app.route('/vistaempleado')
def vistaempleado():
    registros = empleado_facade.obtener_empleados()
    return jsonify(registros)
    
@app.route('/eliminarempleado/<int:id>', methods=['POST'])
def eliminarempleado(id):
    resultado=empleado_facade.eliminar_empleado(id)
    if resultado >0:
        message=f'¡Se elimino exitosamente el ID {id}'
        pusher_client.trigger('my-channel', 'my-event', {'message': f'Empleado eliminado: {id}'})
        return jsonify({"message": message}), 200
    else:
        return jsonify({"message": f"Error al eliminar el ID {id}"}),500
    
@app.route('/editarempleado/<int:id>', methods=['GET','POST'])
def editarempleado(id, message=None):
    con= None
    registros=[]
    try:
        con = mysql.connector.connect(
                host = "185.232.14.52",
                database = "u760464709_vzqzluna_bd",
                user = "u760464709_vzqzluna_usr",
                password = "g4iqen$H"
        )
        if not con.is_connected():
            raise msql.connector.Error('No se pudo conectar a la base de datos')
        
        cursor = con.cursor()
        sql= "SELECT * FROM empleados WHERE Id_Empleado= %s"
        cursor.execute(sql,(id,))
        registros = cursor.fetchall()
        if len(registros)==0:
            message="No se encontro registro con este ID"
            return render_template('editar-empleado.html', message=message, registros=[])
        print("Registros obtenidos:", registros)
    except mysql.connector.Error as err:
        print("Error al conectar con MySQL:", err)
        registros = []  
        message="No se pudo conectar. Verificar conexión."
    finally:
        if con and con.is_connected():
            cursor.close()
            con.close()
    
    return render_template('editar-empleado.html', registros=registros, message=message)
@app.route('/actualizarempleado/<int:id>', methods=['GET','POST'])
def actualizarempleado(id):
    con=None 
    if request.method=='POST':
        Nuevo_Nombre=request.form['txtnombre']
        Nuevo_numeroempleado=request.form['txtnumempleado']
        Nuevo_tel=request.form['txttel']
        Nuevo_domicilio= request.form['txtdomicilio']
        Nuevo_curp=request.form['txtcurp']
        Nuevo_nss=request.form['txtnss']
        Nuevo_rfc=request.form['txtrfc']
        Nuevo_correo= request.form['txtcorreo']
        try:
            con = mysql.connector.connect(
                host = "185.232.14.52",
                database = "u760464709_vzqzluna_bd",
                user = "u760464709_vzqzluna_usr",
                password = "g4iqen$H"
            )
            cursor = con.cursor()
            sql = "UPDATE empleados SET Nombre_Empleado=%s, Numero_Empleado=%s,Telefono=%s, Domicilio=%s, CURP=%s, NSS=%s, RFC=%s, Correo=%s WHERE Id_Empleado= %s"
            cursor.execute(sql,(Nuevo_Nombre, Nuevo_numeroempleado, Nuevo_tel,Nuevo_domicilio,Nuevo_curp,Nuevo_nss,Nuevo_rfc,Nuevo_correo, id,))
            con.commit()
            con.close()     
            message = '¡Registro modificado exitosamente!'
            pusher_client.trigger('my-channel', 'my-event', {'message': f'Nuevo evento: {Nuevo_Nombre}, {Nuevo_numeroempleado}, {Nuevo_tel}, {Nuevo_domicilio},{Nuevo_curp},{Nuevo_nss},{Nuevo_rfc},{Nuevo_correo}'})
        except mysql.connector.Error as err:
            print("Error al modificar con MySQL:", err)
            message="Error al modificar"
        finally:
            if con and con.is_connected():
                cursor.close()
                con.close()
        return editarempleado(id, message=message)
    return editarempleado(id) 



@app.route('/mantenimiento', methods=["GET", "POST"])
def mantenimiento():
    con = None
    message = ""
    maquinas = []
    mantenimientos = []  
    
    try:
        con = mysql.connector.connect(
                host = "185.232.14.52",
                database = "u760464709_vzqzluna_bd",
                user = "u760464709_vzqzluna_usr",
                password = "g4iqen$H"
        )
        cursor = con.cursor(dictionary=True)
        

        cursor.execute("SELECT Id_Maquina, Nombre FROM maquinas")
        maquinas = cursor.fetchall()

        cursor.execute("SELECT * FROM mantenimiento_realizada ORDER BY ID_Mantenimiento DESC")
        mantenimientos = cursor.fetchall() 
        
        print("Mantenimientos:", mantenimientos) 
        
    except mysql.connector.Error as err:
        print(f"Error al conectar a MySQL: {err}")
    
    finally:
        if con and con.is_connected():
            cursor.close()
            con.close()
    
    return render_template('mantenimiento.html', maquinas=maquinas, mantenimientos=mantenimientos, message=message)


@app.route('/eventomantenimiento', methods=["GET", "POST"])
def eventomantenimiento():
    nombre = request.form['txtnombremaquina']
    horometro = int(request.form['txthorometro'])
    fecha = request.form['txtfecha']
    incremento = int(request.form['txtincremento'])
    descripcion = request.form['txtdescripcion']

    

    limite_mantenimiento = horometro + incremento
    tiempo_restante = limite_mantenimiento - horometro
    sql = """INSERT INTO mantenimiento_realizada 
                 (Id_Maquina, Fecha, Horometro, Limite_Mantenimiento, Tiempo_Restante, Descripcion) 
                 VALUES (%s, %s, %s, %s, %s,%s)
           """
    params = (nombre, fecha, horometro, limite_mantenimiento, tiempo_restante,descripcion)
    notification = f"Nuevo evento: {nombre}, {fecha}, {horometro}"
    request_data = {'query': sql, 'params': params, 'notification': notification}

    handler_chain = BDHandler(
        consultaHandler(
            pusherHandler()
        )
    )
    result = handler_chain.handle(request_data)
    if result.get('error'):
        return jsonify({"error": result['error']}), 500

    try:
        recipient_email = "marianavzz125670@gmail.com"  
        enviar_correo_mantenimiento(nombre, horometro, fecha, descripcion, recipient_email)
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return render_template('mantenimiento.html', message='¡Mantenimiento registrado, pero no se pudo enviar el correo!')

    return render_template('mantenimiento.html', message='¡Mantenimiento registrado y correo enviado!')

@app.route('/calcular-mantenimiento', methods=['POST'])
def mantenimiento_calculo():
    response = {}
    try:
        data = request.json
        fecha = data.get('fecha')
        id_maquina = data.get('id_maquina')
        horometro_usuario = int(data.get('horometro'))
        incremento = int(data.get('incremento'))

        connection = mysql.connector.connect(
                host = "185.232.14.52",
                database = "u760464709_vzqzluna_bd",
                user = "u760464709_vzqzluna_usr",
                password = "g4iqen$H"
        )



        with connection.cursor() as cursor:
            sql_ultimo_mantenimiento = """
                SELECT Horometro FROM mantenimiento_realizada
                WHERE Id_Maquina = %s 
                ORDER BY Fecha DESC LIMIT 1
            """
            cursor.execute(sql_ultimo_mantenimiento, (id_maquina,))
            result_ultimo_mantenimiento = cursor.fetchone()
            ultimo_mantenimiento = result_ultimo_mantenimiento[0] if result_ultimo_mantenimiento else 0

            if data.get('calcular'):
                horometro_calculo = horometro_usuario
                limite_mantenimiento = int(ultimo_mantenimiento) + int(incremento)
                tiempo_mantenimiento_restante = limite_mantenimiento - horometro_calculo

                sql_calculo = """
                    INSERT INTO calculos_mantenimiento (Fecha, Id_Maquina, Horometro_Introduccido, Limite_Mantenimiento, Tiempo_Restante) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_calculo, (fecha, id_maquina, horometro_calculo, limite_mantenimiento, tiempo_mantenimiento_restante))
                connection.commit()
                response['status'] = 'success'
                response['message'] = 'Cálculo almacenado correctamente.'

    except Exception as e:
        response['status'] = 'error'
        response['error'] = f'Error: {str(e)}'
    finally:
        if 'connection' in locals():
            connection.close()

    return jsonify(response)

#este no
@app.route('/registromantenimiento', methods=['POST']) 
def mantenimiento_cal():
    response = {}
    try:
        data = request.json
        fecha = data.get('fecha')
        id_maquina = data.get('id_maquina')
        horometro_usuario = int(data.get('horometro'))
        incremento = int(data.get('incremento'))
        descripcion = data.get('descripcion')

        connection = mysql.connector.connect(
                host="localhost",
                database="proyecto",
                user="root",
                password=""
            )

        with connection.cursor() as cursor:
            sql_ultimo_mantenimiento = """
                SELECT Horometro FROM mantenimiento_realizada
                WHERE Id_Maquina = %s 
                ORDER BY Fecha DESC LIMIT 1
            """
            cursor.execute(sql_ultimo_mantenimiento, (id_maquina,))
            result_ultimo_mantenimiento = cursor.fetchone()
            ultimo_mantenimiento = result_ultimo_mantenimiento[0] if result_ultimo_mantenimiento else 0

            if data.get('calcular'):
                horometro_calculo = horometro_usuario
                limite_mantenimiento = int(ultimo_mantenimiento) + int(incremento)
                tiempo_mantenimiento_restante = limite_mantenimiento - horometro_calculo

                sql_calculo = """
                    INSERT INTO calculos_mantenimiento (Fecha, Id_Maquina, Horometro_Introduccido, Limite_Mantenimiento, Tiempo_Restante) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_calculo, (fecha, id_maquina, horometro_calculo, limite_mantenimiento, tiempo_mantenimiento_restante))
                connection.commit()
                response['status'] = 'success'
                response['message'] = 'Cálculo almacenado correctamente.'

            if data.get('mantenimiento_realizado'):
                horometro_realizado = horometro_usuario

                if horometro_realizado <= ultimo_mantenimiento:
                    response['status'] = 'error'
                    response['error'] = 'El horómetro introducido debe ser mayor que el último registrado.'
                else:
                    limite_mantenimiento = horometro_realizado + incremento
                    tiempo_mantenimiento_restante = limite_mantenimiento - horometro_realizado

                    sql_mantenimiento = """
                        INSERT INTO mantenimiento_realizada (Fecha, Id_Maquina, Horometro,Tiempo_Restante, Descripcion) 
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_mantenimiento, (fecha, id_maquina, horometro_realizado,  tiempo_mantenimiento_restante, descripcion))
                    connection.commit()
                    response['status'] = 'success'
                    response['message'] = 'Datos del mantenimiento guardados correctamente.'

    except Exception as e:
        response['status'] = 'error'
        response['error'] = f'Error: {str(e)}'
    finally:
        if 'connection' in locals():
            connection.close()

    return jsonify(response)

@app.route('/eliminarmantenimientodelamaquina/<int:id>', methods=['POST'])
def eliminarmantenimiento(id):
    try:
        print(f"Recibiendo ID de mantenimiento: {id}") 
        handler_chain = BDHandler(
            eliminarHandler(
                pusherHandlerID()
            )
        )
        request_data = {'id': id}
        result = handler_chain.handle(request_data)

        if 'error' in result:
            return jsonify({"error": result['error']}), 500

        return jsonify({"message": "Mantenimiento eliminado correctamente"}), 200

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/vistamantenimiento')
def vistamantenimiento():
    maquinaId = request.args.get('maquinaId')  # Obtener el ID de la máquina desde la consulta GET
    mantenimientos = []  
    
    try:
        con = mysql.connector.connect(
                host = "185.232.14.52",
                database = "u760464709_vzqzluna_bd",
                user = "u760464709_vzqzluna_usr",
                password = "g4iqen$H"
        )
        cursor = con.cursor(dictionary=True)

        if maquinaId:  # Si se pasa el ID de la máquina, filtrar por ese ID
            query = """
                SELECT 
                    m.Id_Mantenimiento, 
                    m.Fecha, 
                    m.Horometro, 
                    m.Limite_Mantenimiento, 
                    m.Tiempo_Restante, 
                    m.Descripcion,
                    ma.Nombre AS Nombre_Maquina 
                FROM 
                    mantenimiento_realizada m
                JOIN 
                    maquinas ma ON m.Id_Maquina = ma.Id_Maquina
                WHERE 
                    ma.Id_Maquina = %s
                ORDER BY 
                    m.Id_Mantenimiento DESC
            """
            cursor.execute(query, (maquinaId,))
        else:  # Si no se pasa un ID, mostrar todos los mantenimientos
            query = """
                SELECT 
                    m.Id_Mantenimiento, 
                    m.Fecha, 
                    m.Horometro, 
                    m.Limite_Mantenimiento, 
                    m.Tiempo_Restante, 
                    m.Descripcion,
                    ma.Nombre AS Nombre_Maquina 
                FROM 
                    mantenimiento_realizada m
                JOIN 
                    maquinas ma ON m.Id_Maquina = ma.Id_Maquina
                ORDER BY 
                    m.Id_Mantenimiento DESC
            """
            cursor.execute(query)
        
        mantenimientos = cursor.fetchall()
        
    except mysql.connector.Error as err:
        print(f"Error al conectar a MySQL: {err}")
    
    finally:
        if con and con.is_connected():
            cursor.close()
            con.close()

    return jsonify(mantenimientos)
@app.route('/getMaquinas')
def get_maquinas():
    maquinas = []
    try:
        con = mysql.connector.connect(
                host = "185.232.14.52",
                database = "u760464709_vzqzluna_bd",
                user = "u760464709_vzqzluna_usr",
                password = "g4iqen$H"
        )
        cursor = con.cursor(dictionary=True)

        cursor.execute("SELECT Id_Maquina, Nombre FROM maquinas")
        maquinas = cursor.fetchall()
        
    except mysql.connector.Error as err:
        print(f"Error al conectar a MySQL: {err}")
    
    finally:
        if con and con.is_connected():
            cursor.close()
            con.close()

    return jsonify(maquinas)

@app.route("/tablamantenimiento")
def indexmantenimiento():
    con=None
    try:
        con = mysql.connector.connect(
                host = "185.232.14.52",
                database = "u760464709_vzqzluna_bd",
                user = "u760464709_vzqzluna_usr",
                password = "g4iqen$H"
            )
    except mysql.connector.Error as err:
        print("Error al conectar:", err)
        return "No se pudo conectar. Verifique su conexion", 500
    finally:
        if con and con.is_connected():
            con.close()
    return render_template("historialmantenimiento.html")

















@app.route('/holamundo')
def hello_world():
    return 'Hola, mundo'

@app.route('/')
def formulario():
    return render_template('formulario.html')

@app.route('/editar/<int:id>', methods=['GET','POST'])
def editar(id, message=None):
    con= None
    registros=[]
    try:
        con = mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF="
        )
        if not con.is_connected():
            raise msql.connector.Error('No se pudo conectar a la base de datos')
        
        cursor = con.cursor()
        sql= "SELECT * FROM tst0_experiencias WHERE Id_Experiencia= %s"
        cursor.execute(sql,(id,))
        registros = cursor.fetchall()
        if len(registros)==0:
            message="No se encontro registro con este ID"
            return render_template('editar.html', message=message, registros=[])
        print("Registros obtenidos:", registros)
    except mysql.connector.Error as err:
        print("Error al conectar con MySQL:", err)
        registros = []  
        message="No se pudo conectar. Verificar conexión."
    finally:
        if con and con.is_connected():
            cursor.close()
            con.close()
    
    return render_template('editar.html', registros=registros, message=message)

@app.route("/tabla")
def index():
    con=None
    try:
        con = mysql.connector.connect(
            host="185.232.14.52",
            database="u760464709_tst_sep",
            user="u760464709_tst_sep_usr",
            password="dJ0CIAFF="
            )
    except mysql.connector.Error as err:
        print("Error al conectar:", err)
        return "No se pudo conectar. Verifique su conexion", 500
    finally:
        if con and con.is_connected():
            con.close()
    return render_template("calificaciones.html")


@app.route('/evento', methods=["GET","POST"])
def evento():
    con= None
    message=""
    if request.method=='POST':
        nombre=request.form['txtnombreApellido']
        comentario=request.form['txtcomentario']
        calificacion=request.form['txtcalificacion']
        
        try:
            con = mysql.connector.connect(
            host="185.232.14.52",
            database="u760464709_tst_sep",
            user="u760464709_tst_sep_usr",
            password="dJ0CIAFF="
            )
            cursor = con.cursor()
            sql = "INSERT INTO tst0_experiencias (Nombre_Apellido, Comentario, Calificacion) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre,comentario,calificacion))
            con.commit()
            con.close()
            message = '¡Encuesta enviada exitosamente!'
            pusher_client.trigger('my-channel', 'my-event', {'message': f'Nuevo evento: {nombre}, {comentario}, {calificacion}'})
        except mysql.connector.Error as err:
            print("error al conectar msql:", err)
            message="Error al enviar encuesta"
        finally:
             if con:
                cursor.close()
                con.close()
        
        return render_template('formulario.html', message=message)
    return render_template('formulario.html')

@app.route('/vista')
def vistatabla():
    try:
        con = mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF="
        )
        cursor = con.cursor()
        cursor.execute("SELECT * FROM tst0_experiencias ORDER BY Id_Experiencia DESC")    
        registros = cursor.fetchall()
        print("Registros obtenidos:", registros)
    except mysql.connector.Error as err:
        print("Error al conectar con MySQL:", err)
        registros = []  
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
    
    return jsonify(registros)


@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    try:
        con = mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF="
        )
        cursor = con.cursor()
        sql = "DELETE FROM tst0_experiencias WHERE Id_Experiencia= %s"
        cursor.execute(sql,(id,))
        con.commit()
        print(cursor.rowcount, "Eliminacion exitosa")
        pusher_client.trigger('my-channel', 'my-event', {'message': f'Nuevo evento: {id}'})
        return '', 200
    except mysql.connector.Error as err:
        print("Error al eliminar con MySQL:", err)
        return '', 500
    finally:
         if con.is_connected():
            cursor.close()
            con.close()
            
    #return redirect(url_for('vistatabla'))
@app.route('/actualizar/<int:id>', methods=['GET','POST'])
def actualizar(id):
    con=None 
    if request.method=='POST':
        Nuevo_nombre=request.form['txtnombreApellido']
        Nuevo_comentario=request.form['txtcomentario']
        Nuevo_calificacion=request.form['txtcalificacion']
        try:
            con = mysql.connector.connect(
            host="185.232.14.52",
            database="u760464709_tst_sep",
            user="u760464709_tst_sep_usr",
            password="dJ0CIAFF="
            )
            cursor = con.cursor()
            sql = "UPDATE tst0_experiencias SET Nombre_Apellido=%s, Comentario=%s, Calificacion=%s WHERE Id_Experiencia= %s"
            
            cursor.execute(sql,(Nuevo_nombre, Nuevo_comentario, Nuevo_calificacion, id,))
            con.commit()
            con.close()     
            message = '¡Encuesta modificada exitosamente!'
            pusher_client.trigger('my-channel', 'my-event', {'message': f'Nuevo evento: {Nuevo_nombre}, {Nuevo_comentario}, {Nuevo_calificacion}'})
        except mysql.connector.Error as err:
            print("Error al modificar con MySQL:", err)
            message="Error al modificar"
        finally:
            if con and con.is_connected():
                cursor.close()
                con.close()
        return editar(id, message=message)
    return editar(id)    

if __name__ == '__main__':
    app.run(debug=True)
