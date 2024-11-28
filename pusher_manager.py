import pusher

class PusherManager:
    def __init__(self):
        self.pusher_client =  pusher.Pusher(
            app_id='1864238',
            key='2ea386b7b90472052932',
            secret='578df1dc2b254c75c850',
            cluster='us2',
            ssl=True
        )

    def enviar_evento(self, canal, evento, data):
        try:
            self.pusher_client.trigger(canal, evento, data)
            print(f"Evento enviado al canal {canal}: {evento}")
        except Exception as e:
            print(f"Error al enviar evento Pusher: {str(e)}")
