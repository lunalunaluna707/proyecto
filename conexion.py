class Conexion:
    @staticmethod
    def create_connection(db_type='mysql'):
        if db_type == 'mysql':
            return connBD()
        else:
            raise ValueError("Tipo de base de datos no soportado")
