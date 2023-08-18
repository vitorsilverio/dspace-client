from rich.console import Console
from fastapi import FastAPI
from fastapi.responses import HttpResponse
from httpx import Client
from urllib.parse import parse_qs, ParseResultBytes, urlencode
from uvicorn import Server, Config


class OpenID_Connector:

    def __init__(self, url: ParseResultBytes, port: int = 8000):
        self.__app = FastAPI()
        self.__console = Console()
        self.__http_client = Client()
        self.__url = url
        self.__code = None
        config = Config(self.__app, "0.0.0.0", port)
        self.__server = Server(config)

        @self.__app.get("/callback")
        async def callback(code: str) -> HttpResponse:
            self.__code = code
            self.__server.shutdown()
            return HttpResponse("""
                <strong>You can close this page now</strong>
            """)

    def login(self) -> str | None:
        query = parse_qs(self.__url.query)
        query["redirect_uri"] = f"http://localhost:{self.__port}/callback"
        self.__url.query = urlencode(query)
        self.__console.print(f"[bold]Attention![/bold]\nOpen {self.__url.geturl()} in your browser to continue")
        self.__server.run()
        return self.__code
