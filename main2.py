from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import string 
import random
import chess_engine

app = FastAPI()
games = {}

class ConnectionManager:
    def __init__(self):
        # active_rooms should contain a dictionary off game_code's which contains another dictioanry 
        # - containing the colours of the player and their respective websocket, (white and black for 1 game)
        self.active_rooms = {}

    async def connection(self, game_code, websocket : WebSocket):
        # accepts the connection for the websocket
        await websocket.accept()
        # for new games, adds the game_code (room) into the active games library
        if game_code not in self.active_rooms:
            self.active_rooms[game_code] = {}
        # first player joining is 'black', and assigned websocket as black
        if "black" not in self.active_rooms:
            self.active_rooms[game_code]["black"] = websocket
            # returns 1 to indicate the colour in websocket_endpoint function
            return 1
        # second player joining is 'white'. and assigned websocket as white
        elif "white" not in self.active_rooms:
            self.active_rooms[game_code]["white"] = websocket
            return -1
        # for normal moves after initilisation, it's 0 (nothing needed to be used for later in main.py)
        else:
            return 0
 
    def disconection(self, game_code, websocket : WebSocket):
        if game_code in self.active_rooms:
            for colour, socket in list[self.active_rooms[game_code].items()]:
                if socket == websocket:
                    # colour used so teh websocket for that specific player is deleted and not whole room
                    del self.active_rooms[game_code][colour]
            if not self.active_rooms[game_code]:
                del self.active_rooms[game_code]


    async def send_online(self, game_code, payload):
        if game_code in self.active_rooms:
            # '.values()' returns the values of a specified dictionary 
            # so payload is sent to both players websockets (black and white)
            for socket in self.active_rooms[game_code].values():
                await socket.send_json(payload)

manager = ConnectionManager()

def random_code():
    letters_num = string.ascii_uppercase + string.digits + string.ascii_uppercase
    code = random.choices(letters_num,k=6)
    return "".join(code)

@app.websocket("/create_game")
def create_game():
    game_code = random_code()
    games[game_code] = chess_engine.game()
    return {"game_code" : game_code}

@app.websocket("/wb/{game_code}")
async def websocket_endpoint(game_code, websocket : WebSocket):
    if game_code not in games:
        await websocket.close(code=4004)
        return

    

