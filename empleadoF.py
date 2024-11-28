from empleadoDAO import EmpleadoDAO

class empleadoFacade:
    def __init__(self, host, database, user, password):
        self.dao = EmpleadoDAO(host, database, user, password)

    def obtener_empleados(self):
        return self.dao.obtener_datos()

    def agregar_empleado(self, datos_empleado):
        return self.dao.insertar(datos_empleado)

    def eliminar_empleado(self, id_empleado):
        return self.dao.eliminar(id_empleado)
