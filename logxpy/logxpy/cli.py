"""CLI commands."""
from __future__ import annotations
import asyncio
from pathlib import Path
import typer
from rich.console import Console

app = typer.Typer(name="loggerx", help="Log viewer")
console = Console()

@app.command()
def tail(file: Path, follow: bool = True, level: str = "DEBUG"):
    """Tail log file."""
    asyncio.run(_tail(file, follow, level))

@app.command()
def serve(file: Path, port: int = 8080, host: str = "localhost"):
    """Start WebSocket server."""
    asyncio.run(_serve(file, host, port))

async def _tail(file: Path, follow: bool, level: str):
    import orjson
    from ._types import Level
    min_level = Level[level.upper()]
    
    async def read():
        with open(file) as f:
            if follow:
                f.seek(0, 2)  # End of file
            while True:
                line = f.readline()
                if line:
                    yield orjson.loads(line)
                elif follow:
                    await asyncio.sleep(0.1)
                else:
                    break
    
    async for record in read():
        if Level[record.get('level', 'INFO')] >= min_level:
            console.print(f"[{record['level']}] {record.get('message', '')} {record}")

async def _serve(file: Path, host: str, port: int):
    from fastapi import FastAPI, WebSocket
    import uvicorn
    
    srv = FastAPI()
    conns: list[WebSocket] = []
    
    @srv.websocket("/ws")
    async def ws(websocket: WebSocket):
        await websocket.accept()
        conns.append(websocket)
        try:
            while True: await websocket.receive_text()
        except: conns.remove(websocket)
    
    uvicorn.run(srv, host=host, port=port)

if __name__ == "__main__":
    app()
