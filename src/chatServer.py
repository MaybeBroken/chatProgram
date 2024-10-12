from os import system

try:
    import websockets
except:
    system(f"python3 -m pip install websockets")
import time as t

try:
    import json as js
except:
    system(f"python3 -m pip install json")
import asyncio

try:
    from panda3d.core import *
except:
    system(f"python3 -m pip install panda3d")
from panda3d.core import TextNode, loadPrcFile
from direct.showbase.ShowBase import ShowBase
from direct.stdpy.threading import Thread
from direct.gui.DirectGui import *

import subprocess

portNum = 8765

exampleMsg = {"time": "literally first lol", "usr": "MaybeBroken", "text": "first"}

devMode = False
anyAuth = True
register_reset = False
chatRooms = [
    {"roomName": "hangout", "messages": [exampleMsg]},
    {"roomName": "spam", "messages": [exampleMsg]},
]
accounts = {"noAuth-(!!)": ""}

for resource in ["./accounts.dat", "./backup.dat"]:
    try:

        with open(resource, "x+t") as i:
            if resource == "./backup.dat":
                i.write(js.encoder.JSONEncoder().encode(o=chatRooms))
            elif resource == "./accounts.dat":
                i.write(js.encoder.JSONEncoder().encode(o=accounts))
    except:
        ...


loadPrcFile("settings.prc")


def parseMessage(msg: str):
    parseMsg: dict = js.decoder.JSONDecoder().decode(s=msg)
    for chatRoom in chatRooms:
        if chatRoom["roomName"] == parseMsg["roomName"]:
            chatRoom["messages"].append(
                {
                    "time": f"{t.localtime()[1]}/{t.localtime()[2]}/{t.localtime()[0]} at {t.localtime()[3]}:{t.localtime()[4]}:{t.localtime()[5]}",
                    "usr": parseMsg["usr"],
                    "text": parseMsg["text"],
                }
            )


def newRoom(msg):
    global register_reset
    for room in chatRooms:
        try:
            room[msg]
            i = 0
            while True:
                i += 1
                try:
                    room[f"{msg} {i}"]
                    chatRooms.append(
                        {f"roomName": f"{msg} {i}", "messages": [exampleMsg]}
                    )
                    break
                except:
                    ...
        except:
            chatRooms.append({"roomName": msg, "messages": [exampleMsg]})
    register_reset = True


def newAccount(name, password):
    global accounts
    accounts[name] = password


def delAccountAuth(name, password):
    global accounts
    if accounts[name] == password:
        del accounts[name]


def delAccountNoAuth(name):
    global accounts
    del accounts[name]


def delRoom(roomName):
    global register_reset
    for room in chatRooms:
        if room["roomName"] == roomName:
            chatRooms.remove(room)
    register_reset = True


def clearRoom(roomName):
    for room in chatRooms:
        if room["roomName"] == roomName:
            room["messages"] = [exampleMsg]


def controlLoop():
    global anyAuth
    authMGR = False
    while True:
        _in = input()
        if _in == "help":
            print(
                f"\n{'='*20}\nSERVER COMMANDS:\nnewRoom: creates a new room\ndelRoom: deletes a room\nauthMgr: runs the authMgr\n{'='*20}"
            )
        elif _in == "newRoom":
            newRoom(input("new room name: "))
        elif _in == "delRoom":
            print([room["roomName"] for room in chatRooms])
            delRoom(input("room to delete: "))
        elif _in == "authMgr":
            authMGR = True
            print(f"ANYAUTH (!): {anyAuth}")
            while authMGR:
                _in = input("| ")
                if _in == "help":
                    print(
                        "| listAccounts: show a list of all registered users\n| toggleAuth: toggles AUTH for clients\n| newAccount: makes an account with the specified name and password\n| delAccount: deletes an account\n| exit: exits the authMgr"
                    )
                if _in == "exit":
                    print("| closing...\n^")
                    authMGR = False
                if _in == "listAccounts":
                    print(f"|{'='*20}|")
                    for account in accounts:
                        print(f"| |-->{account}, {accounts[account]}")
                    print(f"|{'='*20}|")
                if _in == "newAccount":
                    newAccount(
                        input("| -> account name:"), input("| -> account password:")
                    )
                if _in == "delAccount":
                    delAccountNoAuth(input("| -> name of user to delete: "))
                if _in == "toggleAuth":
                    if (
                        input(
                            "| WARNING: this can make it so users are unable to log in. are you sure?\n| enter anything to cancel, otherwise press enter: "
                        )
                        == ""
                    ):
                        if not anyAuth:
                            anyAuth = True
                            print("| -> AUTH: disabled")
                        elif anyAuth:
                            anyAuth = False
                            print("| -> AUTH: enabled")


async def _echo(websocket):
    try:
        msg = await websocket.recv()
        encoder = js.encoder.JSONEncoder()
        if msg == "!!#update":
            await websocket.send(encoder.encode(o=chatRooms))
        elif msg[0] == "+" and msg[1] == "@":
            if anyAuth:
                msg = msg.splitlines()
                await websocket.send("!!#authDisabled")
            else:
                try:
                    msg = msg.splitlines()
                    try:
                        i = accounts[msg[1]]
                        if accounts[msg[1]] == msg[2]:
                            await websocket.send("!!#authSuccess")
                        else:
                            await websocket.send("!!#wrongPassword")
                    except:
                        await websocket.send("!!#wrongUsrname")
                except:
                    print(f"STUPID SERVER BROKE:\nmsg-->{msg}\naccounts-->{accounts}")
                    await websocket.send("!!#internalErr")
        elif msg[0] == "=" and msg[1] == "@":
            if anyAuth:
                msg = msg.splitlines()
                await websocket.send("!!#authDisabled")
            else:
                try:
                    msg = msg.splitlines()
                    newAccount(msg[1], msg[2])
                    await websocket.send("!!#authSuccess")
                except:
                    print(f"STUPID SERVER BROKE:\nmsg-->{msg}\naccounts-->{accounts}")
                    await websocket.send("!!#internalErr")
        else:
            parseMessage(msg)
            print(msg)
            await websocket.send(encoder.encode(o=chatRooms))
    except:
        ...


async def _buildServe():
    async with websockets.serve(_echo, "localhost", int(portNum)):
        print(f"*********\n:SERVER (notice): listening on port {portNum}\n*********")
        await asyncio.Future()


def startLocaltunnel():
    script = f"""
#!/bin/zsh
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
npx localtunnel -p {portNum} -s maybebroken
"""

    try:
        with open("loca.zsh", "xw") as file:
            None
    except:
        ...
    with open("loca.zsh", "w") as file:
        file.write(script)

    subprocess.run(["chmod", "+x", "loca.zsh"])
    result = subprocess.run(
        ["./loca.zsh"], stdout=subprocess.PIPE, shell=True, text=True
    )

    print(result.stdout)


def saveServer():
    while True:
        for resource in ["./accounts.dat", "./backup.dat"]:
            try:
                with open(resource, "wt") as i:
                    if resource == "./backup.dat":
                        i.write(js.encoder.JSONEncoder().encode(o=chatRooms))
                    elif resource == "./accounts.dat":
                        i.write(js.encoder.JSONEncoder().encode(o=accounts))
            except:
                ...
        t.sleep(3)


if not devMode:
    Thread(target=startLocaltunnel).start()
with open("./backup.dat", "rt") as backup:
    chatRooms = js.decoder.JSONDecoder().decode(s=backup.read())
with open("./accounts.dat", "rt") as backup:
    accounts = js.decoder.JSONDecoder().decode(s=backup.read())
Thread(target=saveServer).start()
Thread(target=controlLoop).start()
Thread(target=asyncio.run, args=[_buildServe()]).start()


class chatApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setupMenuGui()

    def update(self, task):
        global chatRooms, roomName
        for room in chatRooms:
            if room["roomName"] == roomName:
                messages = ""
                for message in room["messages"]:
                    messages += f"| {message['time']} | {message['usr']}\n|  {message['text']}\n\n"
                self.currentRoomFrame[1]["text"] = messages
                self.currentRoomFrame[1].setPos(
                    -0.5, 0.07 * len(messages.splitlines()) + self.scrollAmount
                )
        self.updateRooms()
        return task.cont

    def moveTextUp(self):
        self.scrollAmount -= 0.07

    def moveTextDown(self):
        self.scrollAmount += 0.07

    def updateRooms(self):
        global register_reset
        if register_reset:
            self.guiFrame.destroy()
            self.buildMainGUI()
            register_reset = False

    def changeRoom(self, room):
        self.currentRoomFrame[1].hide()
        self.currentRoomFrame = [item for item in self.roomsList if room in item[0]]
        self.currentRoomFrame = self.currentRoomFrame[0][1]
        global roomName
        roomName = room
        self.currentRoomFrame[1].show()

    def setupMenuGui(self):
        self.set_background_color(0.2, 0.2, 0.3, 1)
        self.startService()

    def newRoomGUI(self):
        self.newRoomTextBar = DirectEntry(
            parent=self.guiFrame,
            text="",
            scale=0.06,
            command=newRoom,
            numLines=1,
            pos=(-0.6, 0, -0.8),
            cursorKeys=1,
            overflow=0,
        )

    def buildMainGUI(self):
        self.guiFrame = DirectFrame(parent=self.aspect2d)
        self.roomFrame = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-1, -0.65, -1, 1),
            frameColor=(0.15, 0.15, 0.2, 1),
        )
        self.lobbyFrame = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-0.64, 1, -1, 1),
            pos=(0, -1, 0),
            frameColor=(0.3, 0.3, 0.3, 1),
        )
        self.newRoom = DirectButton(
            parent=self.roomFrame,
            pos=(-0.82, 1, -0.8),
            scale=0.06,
            text="New Room",
            command=self.newRoomGUI,
        )
        self.currentRoomFrame = None
        posIndex = 0
        defaultDistance = 0.12
        self.roomsList = []

        for room in chatRooms:
            name = room["roomName"]
            newRoomButton = DirectButton(
                parent=self.roomFrame,
                pos=(-0.85, 1, 0.9 - (defaultDistance * posIndex)),
                scale=0.06,
                text=name,
                command=self.changeRoom,
                extraArgs=[name],
            )
            delRoomButton = DirectButton(
                parent=self.roomFrame,
                pos=(-1.05, 1, 0.9 - (defaultDistance * posIndex)),
                scale=0.06,
                text="del",
                command=delRoom,
                extraArgs=[name],
            )

            messages = ""
            for message in room["messages"]:
                messages += f"| {message['usr']}\n|  --> {message['text']}\n\n"
            messageText = OnscreenText(
                parent=self.lobbyFrame,
                text=messages,
                pos=(-0.5, 0.07 * len(messages.splitlines())),
                scale=0.07,
                align=TextNode.ALeft,
                wordwrap=20,
            )
            messageText.hide()
            self.roomsList.append([name, [newRoomButton, messageText, delRoomButton]])
            posIndex += 1
        self.currentRoomFrame = self.roomsList[0][1]
        self.currentRoomFrame[1].show()
        global roomName
        roomName = self.roomsList[0][0]
        self.scrollAmount = 0
        self.accept("wheel_up", self.moveTextUp)
        self.accept("wheel_down", self.moveTextDown)

    def startService(self):
        self.buildMainGUI()
        self.taskMgr.add(self.update, "update")


chatapp = chatApp()
chatapp.run()
