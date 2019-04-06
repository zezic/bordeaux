import uvicorn
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.responses import JSONResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from sockets.notifier import Notifier
from storage.thread import Thread


def format_datetime(value):
    return value.strftime('%H:%M')

templates = Jinja2Templates(directory='templates')
templates.env.filters['format_datetime'] = format_datetime

app = Starlette(debug=True)
app.mount('/static', StaticFiles(directory='static'), name='static')


thread = Thread()
thread.add_post('Привет')

notifier = Notifier()


@app.route('/api')
async def api_dummy(request):
    return JSONResponse({'hello': 'world'})

@app.route('/')
async def index_page(request):
    return templates.TemplateResponse('index.html', {
        'request': request,
        'thread': thread
    })

@app.route('/thread')
class ThreadOperation(HTTPEndpoint):
    async def post(self, request):
        form = await request.form()
        text = form['text']
        new_post = thread.add_post(text)
        await notifier.notify_listeners({
            'datetime': format_datetime(new_post.datetime),
            'text': new_post.text
        })
        return RedirectResponse(url='/')

@app.websocket_route('/ws')
class WebSocketNotifier(WebSocketEndpoint):
    async def on_connect(self, websocket):
        await websocket.accept()
        notifier.add_listener(websocket)

    async def on_disconnect(self, websocket, close_code):
        notifier.remove_listener(websocket)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
