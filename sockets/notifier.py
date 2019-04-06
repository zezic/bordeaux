class Notifier():
    def __init__(self):
        self.listeners = []

    def add_listener(self, websocket):
        self.listeners.append(websocket)

    def remove_listener(self, websocket):
        self.listeners.remove(websocket)

    async def notify_listeners(self, text):
        for websocket in self.listeners:
            await websocket.send_text(text)
