from conexion import Conexion

class consultaMaquina:
    def __init__(self):
        self.db = Conexion.create_connection('mysql')
        self.con = self.db.connect() if self.db else None

    def obtener_maquinas(self):
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
        except mysql.connector.Error as err:
            print("Error al conectar con MySQL:", err)
        finally:
            if self.con and self.con.is_connected():
                cursor.close()
                self.db.close()
        return registros


class InsertarNuevaMaquina:
    def __init__(self):
        self.db = Conexion.create_connection('mysql')
        self.con = self.db.connect() if self.db else None

    def insertar(self, nombre, placas, linea, marca, modelo, serie, imagen):
        try:
            if self.con:
                cursor = self.con.cursor()
                query = "INSERT INTO maquinas (Nombre, Placas, Linea, Marca, Modelo, Serie, Imagen) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                values = (nombre, placas, linea, marca, modelo, serie, imagen)
                cursor.execute(query, values)
                self.con.commit()  # Confirmamos los cambios
                print("Máquina insertada con éxito")
        except mysql.connector.Error as err:
            print(f"Error al insertar máquina: {err}")
        finally:
            if self.con and self.con.is_connected():
                cursor.close()
                self.db.close()


class MaquinaActualizar:
    def __init__(self):
        self.db = Conexion.create_connection('mysql')
        self.con = self.db.connect() if self.db else None

    def actualizar(self, id_maquina, nombre, placas, linea, marca, modelo, serie, imagen):
        try:
            if self.con:
                cursor = self.con.cursor()
                query = """UPDATE maquinas 
                           SET Nombre=%s, Placas=%s, Linea=%s, Marca=%s, Modelo=%s, Serie=%s, Imagen=%s 
                           WHERE Id_Maquina=%s"""
                values = (nombre, placas, linea, marca, modelo, serie, imagen, id_maquina)
                cursor.execute(query, values)
                self.con.commit()
                print(f"Máquina con ID {id_maquina} actualizada con éxito")
        except mysql.connector.Error as err:
            print(f"Error al actualizar máquina: {err}")
        finally:
            if self.con and self.con.is_connected():
                cursor.close()
                self.db.close()


class MaquinaEliminar:
    def __init__(self):
        self.db = Conexion.create_connection('mysql')
        self.con = self.db.connect() if self.db else None

    def eliminar(self, id_maquina):
        try:
            if self.con:
                cursor = self.con.cursor()
                query = "DELETE FROM maquinas WHERE Id_Maquina=%s"
                values = (id_maquina,)
                cursor.execute(query, values)
                self.con.commit()
                print(f"Máquina con ID {id_maquina} eliminada con éxito")
        except mysql.connector.Error as err:
            print(f"Error al eliminar máquina: {err}")
        finally:
            if self.con and self.con.is_connected():
                cursor.close()
                self.db.close()
