import mysql.connector

class EmpleadoDAO:
    def __init__(self, host, database, user, password):
        self.config = {
            'host': host,
            'database': database,
            'user': user,
            'password': password
        }

    def obtener_datos(self):
        try:
            con = mysql.connector.connect(**self.config)
            cursor = con.cursor()
            cursor.execute("SELECT * FROM empleados")
            registros = cursor.fetchall()
            return registros
        except mysql.connector.Error as err:
            print("Error al conectar con MySQL:", err)
            return []
        finally:
            if con.is_connected():
                cursor.close()
                con.close()

    def insertar(self, empleado):
        try:
            con = mysql.connector.connect(**self.config)
            cursor = con.cursor()
            sql = "INSERT INTO empleados (Nombre_Empleado, Numero_Empleado, Telefono, Domicilio, CURP, NSS, RFC, Correo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, empleado)
            con.commit()
            return cursor.rowcount
        except mysql.connector.Error as err:
            print("Error al insertar:", err)
            return 0
        finally:
            if con.is_connected():
                cursor.close()
                con.close()

    def eliminar(self, id_empleado):
        try:
            con = mysql.connector.connect(**self.config)
            cursor = con.cursor()
            sql = "DELETE FROM empleados WHERE Id_Empleado = %s"
            cursor.execute(sql, (id_empleado,))
            con.commit()
            return cursor.rowcount
        except mysql.connector.Error as err:
            print("Error al eliminar:", err)
            return 0
        finally:
            if con.is_connected():
                cursor.close()
                con.close()
