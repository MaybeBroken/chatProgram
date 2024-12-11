import json
import os
import sys
from threading import Thread
from time import sleep
import websockets
import asyncio
import socket

if sys.platform == "darwin":
    pathSeparator = "/"
elif sys.platform == "win32":
    pathSeparator = "\\"
os.chdir(__file__.replace(__file__.split(pathSeparator)[-1], ""))

serverQueue: dict[dict[str, None]] = {}
messageQueue: list[dict[str, None]] = []
hostname = socket.gethostname()
# IPAddr = socket.gethostbyname(hostname)
IPAddr = "10.0.42.144"
portNum = 8765
send = lambda head, body: messageQueue.append({head: body})


# this is only to be enabled for testing purposes!
HTTPSERVER = True


class CLI:
    class Control:
        def left(num):
            return f"\033[{num}D"

        def right(num):
            return f"\033[{num}C"

        def up(num):
            return f"\033[{num}A"

        def down(num):
            return f"\033[{num}B"

        def changeLineUp(line, len):
            return f"\033[{line}A\033[{len}D"

        def changeLineLeft(len):
            return f"\033[{1}A\033[{len}D"

        def changeLineRight(len):
            return f"\033[{1}A\033[{len}C"

    class Color:
        GREEN = "\033[92m"
        LIGHT_GREEN = "\033[1;92m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
        BLUE = "\033[1;34m"
        MAGENTA = "\033[1;35m"
        BOLD = "\033[;1m"
        CYAN = "\033[1;36m"
        LIGHT_CYAN = "\033[1;96m"
        LIGHT_GREY = "\033[1;37m"
        DARK_GREY = "\033[1;90m"
        BLACK = "\033[1;30m"
        WHITE = "\033[1;97m"
        INVERT = "\033[;7m"
        RESET = "\033[0m"


async def echo(websocket):
    remoteAddr = websocket.remote_address[0]
    clientType = await websocket.recv()
    if clientType == "client":
        while websocket.open:
            try:
                global serverQueue, messageQueue
                await websocket.send(json.JSONEncoder().encode(messageQueue))
                messageQueue = []
                cliReturn = await websocket.recv()
                serverQueue[remoteAddr] = json.JSONDecoder().decode(cliReturn)
                sleep(0.025)
            except (
                websockets.exceptions.ConnectionClosedOK
                or websockets.exceptions.ConnectionClosedError
            ):
                del serverQueue[remoteAddr]
    elif clientType == "admin":
        while websocket.open:
            await websocket.send(json.JSONEncoder().encode(serverQueue))
            sleep(0.025)


async def main(portNum):
    async with websockets.serve(echo, IPAddr, int(portNum)):
        print(
            f"{CLI.Color.RESET}WebSocket server running on {CLI.Color.YELLOW}http://{IPAddr}:{portNum}{CLI.Color.RESET}\n"
        )
        await asyncio.Future()


def startServer(portNum):
    while True:
        asyncio.run(main(portNum))


Thread(target=startServer, args=[portNum], daemon=True).start()
if HTTPSERVER:

    def _response(directory, port):
        from http.server import HTTPServer, SimpleHTTPRequestHandler

        class MyHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)

            def log_message(self, format, *args):
                return

        httpd = HTTPServer((IPAddr, port), MyHandler)
        httpd.serve_forever()

    Thread(target=_response, args=["client/", 8100], daemon=True).start()
    Thread(target=_response, args=["admin/", 8200], daemon=True).start()

    print(
        f"\n{CLI.Color.RESET}HTTP server running on {CLI.Color.GREEN}http://{IPAddr}:8100{CLI.Color.RESET}\n"
    )
    print(
        f"{CLI.Color.RESET}ADMIN server running on {CLI.Color.GREEN}http://{IPAddr}:8200{CLI.Color.RESET}\n"
    )


def inputLoop():
    while True:
        message = input()
        for element in ["EntryBox1", "EntryBox2"]:
            ...
        for client in serverQueue:
            send("EntryBox2", message)


Thread(target=inputLoop).start()

while True:
    try:
        if len(serverQueue) > 0:
            for message in serverQueue.copy():
                print(" " * 100)
            print(CLI.Control.up(len(serverQueue) + 1))
            for message in serverQueue.copy():
                print(f"{message}: {serverQueue[message]}")
            print(CLI.Control.up(len(serverQueue) + 1))
        sleep(0.025)
    except:
        ...
