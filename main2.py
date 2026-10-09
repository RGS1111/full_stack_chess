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
    # based on what connection returns, thats black or white (1 or -1 or 0), 0 if room full
    player = manager.connection(game_code, websocket)

    if player == 0:
        # if there are 2 players here already then reject new connection, as 0 returned when 1 and -1 filled
        await websocket.close(code=4004)
        return 

    game_instance = games[game_code]

    try:
        while True:
            data = await websocket.recieve_json()

            if game_instance.current_player.colour != player:
                await websocket.send_json({
                    "type" : "MOVE INVALID",
                    "reason" : "Not your move!"
                })
                continue
            # if start and end from front end is list format for json, then turn list to tuple
            player_start = tuple(data.get("start")) if isinstance(data.get("start"), list) else data.get("start")
            player_end = tuple(data.get("end")) if isinstance(data.get("end"), list) else data.get("end")
            player_promotion = data.get("promotion")
            recieved_move = game_instance.make_move(player_start, player_end, player_promotion)

            if recieved_move.get("valid"):
                await manager.send_online(game_code, {
                    "type" : "MOVE_SUCCESS",
                    "data" : recieved_move 
                })
            else:
                await websocket.send_json({
                    "type" : "MOVE_INVALID",
                    "reason" : recieved_move.get("reason")
                })

            if recieved_move.playing == False:
                # playing is the flag variable in chess_engine confirming game is stil playing 
                break
    except:
        manager.disconection(game_code, websocket)

    
if __name__ == "__main__":
    Game = chess_engine.game()


    

