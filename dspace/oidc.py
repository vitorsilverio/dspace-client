from rich.console import Console
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from httpx import Client
from urllib.parse import parse_qsl, ParseResultBytes, urlencode
from uvicorn import Server, Config


class OpenID_Connector:

    def __init__(self, url: ParseResultBytes, port: int = 8000):
        self.__app = FastAPI()
        self.__console = Console()
        self.__http_client = Client()
        self.__url = url
        self.__code = None
        self.__port = port
        config = Config(self.__app, "0.0.0.0", port, limit_max_requests=1)
        self.__server = Server(config)

        @self.__app.get("/callback")
        async def callback(code: str) -> HTMLResponse:
            self.__code = code
            return HTMLResponse("""
                <strong>You can close this page now</strong>
            """)

    def login(self) -> str | None:
        query_params = parse_qsl(self.__url.query)
        query = {}
        for k,v in query_params:
            query[k] = v
        query["redirect_uri"] = f"http://localhost:{self.__port}/callback"
        self.__url = self.__url._replace(query=urlencode(query))
        self.__console.print(f"[bold]Attention![/bold]\nOpen the url:\n{self.__url.geturl()}\nto continue")
        self.__server.run()
        return self.__code
