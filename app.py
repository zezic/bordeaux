import typing
import sqlalchemy
import uvicorn
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.datastructures import URL
from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.responses import (
    JSONResponse, PlainTextResponse, RedirectResponse, Response
)
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from urllib.parse import quote_plus

from sockets.notifier import Notifier

from models.board import Board
from models.thread import Thread, ThreadSlugGenerator
from models.post import Post

from db import database, metadata

from markdown.renderer import render_markdown


class RedirectResponseWithBackground(Response):
    def __init__(
        self, url: typing.Union[str, URL], status_code: int = 302, headers: dict = None,
        **kwargs
    ) -> None:
        super().__init__(content=b"", status_code=status_code, headers=headers, **kwargs)
        self.headers["location"] = quote_plus(str(url), safe=":/#?&=@[]!$&'()*+,;")


engine = sqlalchemy.create_engine(str(database.url))
metadata.create_all(engine)


def format_datetime(value):
    return value.strftime('%Y-%m-%d %H:%M:%S')

def get_id(something):
    return hex(id(something))[2:]

def get_hex(integer):
    return hex(integer)

thread_slug_generator = ThreadSlugGenerator()

templates = Jinja2Templates(directory='templates')
templates.env.filters['format_datetime'] = format_datetime
templates.env.filters['id'] = get_id
templates.env.filters['markdown'] = render_markdown
templates.env.filters['hex'] = get_hex

app = Starlette(debug=True)
app.mount('/static', StaticFiles(directory='static'), name='static')

notifier = Notifier()

@app.on_event('startup')
async def create_boards():
    threads = await Thread.objects.all()
    if len(threads) > 0:
        print('Registering {} thread slugs...'.format(len(threads)))
    else:
        print('Preparing free thread slugs...')
    thread_slug_generator.register_threads(threads)

@app.route('/api')
async def api_dummy(request):
    return JSONResponse({'hello': 'world'})

@app.route('/')
async def index_page(request):
    boards = await Board.objects.all()
    return templates.TemplateResponse('index.html', {
        'request': request,
        'boards': boards
    })

@app.route('/create')
class NewBoardEndpoint(HTTPEndpoint):
    async def get(self, request):
        return templates.TemplateResponse('board_creation.html', {
            'request': request
        })

    async def post(self, request):
        form = await request.form()
        try:
            markdown = form['markdown'].strip()
            slug = form['slug'].strip().lower()
            title = form['title'].strip()
        except KeyError:
            return PlainTextResponse(
                'Please, provide the "markdown", "slug" and "title".',
                status_code=400
            )
        if len(markdown) == 0 or len(slug) == 0 or len(title) == 0:
            return PlainTextResponse(
                '"markdown", "slug" and "title" should not be empty.',
                status_code=400
            )
        if slug[:2] == '0x':
            return PlainTextResponse(
                '"slug" should not start from "0x".',
                status_code=400
            )
        board = await Board.objects.filter(slug=slug).exists() or await Board.objects.filter(title=title).exists()
        if board:
            return PlainTextResponse(
                'There is already board with slug "{}" called "{}".'.format(board.slug, board.title),
                status_code=409
            )
        board = await Board.objects.create(
            slug=slug,
            title=title
        )
        thread = await Thread.objects.create(
            slug=thread_slug_generator.get(),
            board=board
        )
        await Post.objects.create(
            thread=thread,
            offset=0,
            markdown=markdown
        )
        return RedirectResponse(url='/{}/{}'.format(
            board.slug, thread.slug
        ))

@app.route('/{board_slug}')
async def board_page(request):
    board = await Board.objects.get(slug=request.path_params['board_slug'])
    threads = await Thread.objects.filter(board=board).all()
    for thread in threads:
        thread.posts = await Post.objects.filter(thread=thread).all()
    return templates.TemplateResponse('board.html', {
        'request': request,
        'board': board,
        'threads': threads
    })

@app.route('/{board_slug}/write')
class NewThreadEndpoint(HTTPEndpoint):
    async def get(self, request):
        board = await Board.objects.get(slug=request.path_params['board_slug'])
        return templates.TemplateResponse('board_posting.html', {
            'request': request,
            'board': board
        })

    async def post(self, request):
        form = await request.form()
        try:
            markdown = form['markdown']
        except KeyError:
            return PlainTextResponse(
                'Please, provide a "markdown" field.',
                status_code=400
            )
        board = await Board.objects.get(slug=request.path_params['board_slug'])
        thread = await Thread.objects.create(
            slug=thread_slug_generator.get(),
            board=board
        )
        await Post.objects.create(
            thread=thread,
            offset=0,
            markdown=markdown
        )
        return RedirectResponse(url='/{}/{}'.format(
            board.slug, thread.slug
        ))

@app.route('/{board_slug}/{thread_slug}')
class ThreadEndpoint(HTTPEndpoint):
    async def get(self, request):
        thread = await Thread.objects.select_related('board').get(slug=request.path_params['thread_slug'])
        thread.posts = await Post.objects.filter(thread=thread).all()
        return templates.TemplateResponse('thread.html', {
            'request': request,
            'board': thread.board,
            'thread': thread
        })

    async def post(self, request):
        thread = await Thread.objects.get(slug=request.path_params['thread_slug'])
        form = await request.form()
        try:
            markdown = form['markdown']
        except KeyError:
            return PlainTextResponse(
                'Please, provide a "markdown" field.',
                status_code=400
            )
        post = await Post.objects.create(
            thread=thread,
            offset=await Post.objects.filter(thread=thread).count(),
            markdown=markdown
        )
        task = BackgroundTask(notifier.notify_listeners, slug=thread.slug, data={
            'offset': post.offset,
            'datetime': format_datetime(post.datetime),
            'html': render_markdown(post.markdown)
        })
        return RedirectResponseWithBackground(
            url='{}#{}'.format(str(request.url).split('#')[0], get_hex(post.offset)),
            background=task
        )

@app.route('/toggle-theme')
class ThemeManager(HTTPEndpoint):
    async def post(self, request):
        response = RedirectResponse(url=request.headers['referer'])
        if request.cookies.get('theme'):
            response.delete_cookie('theme')
        else:
            response.set_cookie('theme', 'default-dark')
        return response

@app.websocket_route('/ws/{thread_slug}')
class WebSocketNotifier(WebSocketEndpoint):
    async def on_connect(self, websocket):
        try:
            slug = websocket.path_params['thread_slug']
        except KeyError:
            return
        await websocket.accept()
        notifier.add_listener(slug, websocket)

    async def on_disconnect(self, websocket, close_code):
        notifier.remove_listener(websocket)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
