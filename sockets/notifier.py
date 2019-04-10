class Notifier():
    def __init__(self):
        self.listeners = {}
        self.slugs = {}

    def add_listener(self, slug, websocket):
        if slug not in self.slugs:
            self.slugs.update({slug: []})
        self.listeners.update({id(websocket): slug})
        self.slugs.get(slug).append(websocket)

    def remove_listener(self, websocket):
        self.slugs.get(self.listeners.get(id(websocket))).remove(websocket)
        self.listeners.pop(id(websocket))

    async def notify_listeners(self, slug, data):
        for websocket in self.slugs.get(slug):
            await websocket.send_json(data)
