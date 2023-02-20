from sys import exit

from typer import Typer
from uvicorn import run

from config import Settings

cli = Typer()


@cli.command()
def runapi(
        host: str = Settings.uvicorn.host,
        port: int = Settings.uvicorn.port,
        reload: bool = Settings.uvicorn.reload,
        log_level: str = Settings.uvicorn.log_level,
        use_colors: bool = Settings.uvicorn.use_colors,
        proxy_headers: bool = Settings.uvicorn.proxy_headers
) -> None:
    run(
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        use_colors=use_colors,
        app=Settings.uvicorn.app,
        proxy_headers=proxy_headers,
        reload_dirs=["src", ]
    )

if __name__ == "__main__":
    exit(cli())
