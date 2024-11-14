from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from flask import jsonify
from datetime import datetime,  timedelta
from flask_cors import CORS
import pusher
import mysql.connector

import pytz

import pusher



app = Flask(__name__) 
CORS(app)
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
                host="localhost",
                database="proyecto",
                user="root",
                password=""
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
    def insertar(self, nombre, placa, modelo, linea, marca, serie):
        sql="""INSERT INTO maquinas(Nombre, Placas, Modelo, Linea, Marca, Serie)
        VALUES (%s, %s, %s, %s, %s, %s)"""
        parametros=(nombre, placa, modelo, linea, marca, serie)
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
           # con.close()
            db.close()
    
    return render_template('maquinas.html', registros=registros)  
@app.route('/vistamaquina')
def vistamaquina():
    consulta= consultaMaquina()
    registros=consulta.maquinas()
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


@app.route('/apartadomaquina')
def apartado_maquina():
    return render_template('apartado_maquina.html')

@app.route('/formmaquina')
def formulariomaquina():
    return render_template('form-maquina.html')

@app.route('/eventomaquina', methods=["GET","POST"])
def eventomaquina():
    #con= None
    message=""
    if request.method=='POST':
        nombremaquina=request.form['txtnombremaquina']
        placa=request.form['txtplaca']
        modelo=request.form['txtmodelo']
        marca=request.form['txtmarca']
        serie=request.form['txtserie']
        linea=request.form['txtlinea']
        db=Conexion.create_connection('mysql')
        con=db.connect()
        if con:
                accion=InsertarNuevaMaquina(db)
                if accion.insertar(nombremaquina,placa,modelo,linea, marca,serie):
                    message = '¡SE REGISTRO EXITOSAMENTE!'
                    pusher_client.trigger('my-channel', 'my-event', {'message': f'Nuevo evento: {nombremaquina}, {placa}, {modelo},{linea},{marca}, {serie}'})
                else:
                    message="Error al registrar maquina"
                db.close()
        return render_template('form-maquina.html', message=message)
    return render_template('form-maquina.html')

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
            #con.close()
    
    return render_template('apartado_maquina.html', registros=registros, mantenimientos=mantenimientos, operador=operador, message=message)



@app.route('/empleados', methods=['GET'])
def empleados():
    registros = []
    db=Conexion.create_connection('mysql')
    con=db.connect()
    try:
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM empleados")  
            registros = cursor.fetchall()
            print("Registros de máquinas obtenidos:", registros)
    except mysql.connector.Error as err:
        print("Error al conectar con MySQL:", err)
        registros = []  
    finally:
        if con and con.is_connected():
            cursor.close()
            db.close()
            #con.close()
    
    return render_template('empleados.html', registros=registros)  

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


@app.route('/eliminarempleado/<int:id>', methods=['POST'])
def eliminarempleado(id):
    try:
        con = mysql.connector.connect(
            host="localhost",
            database="proyecto",
            user="root",
            password=""
        )
        cursor = con.cursor()
        sql = "DELETE FROM empleados WHERE Id_Empleado= %s"
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
