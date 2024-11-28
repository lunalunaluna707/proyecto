import mysql.connector
import pusher

class Handler:
    def __init__(self, successor=None):
        self.successor = successor

    def handle(self, request):
        if self.successor:
            result = self.successor.handle(request)
            if result is None:
                return {"error": "La solicitud no fue manejada correctamente por la cadena."}
            return result
        return {"error": "Fin de la cadena, solicitud no manejada."}


class BDHandler(Handler):
    def handle(self, request):
        try:
            request['con'] = mysql.connector.connect(
                host = "185.232.14.52",
                database = "u760464709_vzqzluna_bd",
                user = "u760464709_vzqzluna_usr",
                password = "g4iqen$H"
            )
            if request['con'].is_connected():
                print("Conexión exitosa a la base de datos")
        except mysql.connector.Error as err:
            return {"error": f"Error de conexión: {err}"}
        if self.successor:
            return self.successor.handle(request)
        return {}

 

class consultaHandler(Handler):
    def handle(self, request):
        try:
            cursor = request['con'].cursor()
            cursor.execute(request['query'], request['params'])
            request['con'].commit()
            print("Consulta ejecutada correctamente")
        except Exception as err:
            return {"error": f"Error al ejecutar la consulta: {err}"}
        if self.successor:
            return self.successor.handle(request)
        return {}

class pusherHandlerID(Handler):
    def __init__(self, successor=None):
        super().__init__(successor)
        self.pusher_client = pusher.Pusher(
            app_id='1864238',
            key='2ea386b7b90472052932',
            secret='578df1dc2b254c75c850',
            cluster='us2',
            ssl=True
        )

    def handle(self, request):
        try:
            print(f"Enviando al mantenimiento con ID: {request['id']}")
            message = f'Nuevo evento: {request["id"]}'
            self.pusher_client.trigger('my-channel', 'my-event', {'message': message})
            print("Enviada correctamente")
        except Exception as e:
            return {"error": f"Error al enviar la notificación: {e}"}
        return super().handle(request)


class pusherHandler(Handler):
    def __init__(self, successor=None):
        super().__init__(successor)
        self.pusher_client = pusher.Pusher(
            app_id='1864238',
            key='2ea386b7b90472052932',
            secret='578df1dc2b254c75c850',
            cluster='us2',
            ssl=True
        )

    def handle(self, request):
        try:
            self.pusher_client.trigger('my-channel', 'my-event', {'message': request['notification']})
            print("Enviada correctamente")
        except Exception as e:
            return {"error": f"Error al enviar: {e}"}
        if self.successor:
            return self.successor.handle(request)
        return {}
    
class eliminarHandler(Handler):
    def handle(self, request):
        try:
            cursor = request['con'].cursor()
            sql = "SELECT * FROM mantenimiento_realizada WHERE Id_Mantenimiento = %s"
            cursor.execute(sql, (request['id'],))
            result = cursor.fetchone()
            
            if not result:
                return {"error": f"No se encontró un mantenimiento con ID: {request['id']} "}
            
            sql = "DELETE FROM mantenimiento_realizada WHERE Id_Mantenimiento = %s"
            cursor.execute(sql, (request['id'],))
            request['con'].commit()
            
            if cursor.rowcount > 0:
                print(f"Eliminación del mantenimiento exitoso: {request['id']} ")
                return {'success': True}  
            else:
                print(f"No se pudo eliminar el mantenimiento con ID: {request['id']}.")
                return {'success': False}  
        except Exception as err:
            return {"error": f"Error al ejecutar la consulta: {err}"}
        return super().handle(request)
