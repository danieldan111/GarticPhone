import socket
import threading
import protocol
from threading import Lock
from loobyUtil import *
from gameUtil import *
from PIL import Image
import io


main_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = ("0.0.0.0", 6060)
HEADER = 3
rooms = {}
mutex_lock = Lock()
min_player_amount = 2 #set to 3


def send_obj(player, obj):
    player.conn.send_obj(obj)
    print(f"[SERVER] Updated {player.name}")

#send Chat object to everyone:
def update_chat(players, chat):
    chats = []
    for item in chat:
        chats.append(item.chat)

    threads = []
    for player in players:
        t = threading.Thread(target=send_obj, args=(player, chats))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    print("[SERVER] finished update")

#game ended: open chat:
def showcase_game(conn, addr, game): 
    chats = game.chats
    update_chat(game.players, chats)
    #send chat to all players


#real game:
def start_game(conn, addr, parms):
    _, roomid = parms
    # for room in rooms:
    room = rooms[roomid]
    players = room.players
    for player in players:
        if player.name == roomid:
            break
    if player.addr != addr:
        return ("EROR", "EROR")
    if room:
        if len(room.players) < min_player_amount:
            print("failed to start")
            return ("EROR", "ERORMinimum number of players is 3")
            
        return ("STRT", room)
    
    return ("EROR", "EROR")


def update_start(room, suggetsions, sentences, game):
    i = 0
    threads = [] 
    for player in room.players:
        if player.name != room.id:
            player.conn.send(f"STRT{suggetsions[i]}")
            i = i + 1
            t = threading.Thread(target=game_client, args=(player, sentences, game))
            t.start()
            threads.append(t)
            print(f"[SERVER] Started Game for {player.name}")
    
    for t in threads:
        t.join()
    
    print(f"[SERVER] all threads for room {room.id} ended")


def end_game(room):
    for player in room.players:
        player.conn.send("END")
        print(f"[SERVER] Updated {player.name}")


def game_started(conn, addr, room):
    #notify players game has started
    game = Game(room.players)
    suggetsions = game.start()
    conn.send(f"CNFM{suggetsions[0]}")
    sentences = {}

    t = threading.Thread(target=update_start, args=(room, suggetsions[1::], sentences, game))
    t.start()
    time.sleep(0.5)
    for player in room.players:
        if player.name == room.id:
            break
    #first sentence
    gameIsGoing = True
    while gameIsGoing:
        msg = conn.recv()
        msgCode = msg[:4]
        if msgCode == "SENT":
            sen = msg[5::]
            sentences[player] = sen
        
        allSubmit = False
        while not allSubmit:
            if game.close: #to change
                print("[SERVER] unexpected error")
                end_game(room)
                return
            time.sleep(0.1)
            allSubmit = len(sentences) == len(room.players)
        
        parms = game.sentences(sentences)
        gameIsGoing = parms[0]
        transport = parms[1]
        for item in transport.keys():
            transport[item].conn.send(sentences[item])
        
        sentences.clear()
        #recv images
        image = conn.recvall()
        sentences[player] = image

        allSubmit = False
        while not allSubmit:
            time.sleep(0.1)
            allSubmit = len(sentences) == len(room.players)
            print(len(sentences))

        # for image in sentences.values():
        #     im = Image.open(io.BytesIO(image))
        #     im.show()
        
        parms = game.images(sentences)
        gameIsGoing = parms[0]
        if not gameIsGoing:
            break
        transport = parms[1]
        for item in transport.keys():
            transport[item].conn.sendall(sentences[item])

        sentences.clear()
        # break
    
    print("game ended")
    t.join()
    #show chat:
    end_game(room)
    print("show chat")
    showcase_game(conn, addr, game)


def game_client(player, sentences, game):
    time.sleep(1)
    conn = player.conn
    conn.send("CNFM")
    rounds = game.rounds
    for i in range(rounds // 2):
        #first sentence
        try:
            msg = conn.recv()
        except Exception as e: #player disconncted
            #close room for all
            game.close = True
            return
        msgCode = msg[:4]
        if msgCode == "SENT":
            sen = msg[5::]
            sentences[player] = sen
        else:
            return
        #submit image
        try:
            image = player.conn.recvall()
        except Exception as e: #player disconncted
            #close room for all
            game.close = True
            return
             
        sentences[player] = image 

    #game ended   
    print("ended")


def print_rooms():
    global rooms
    for room in rooms.values():
        print("room:")
        for player in room.players:
            print(player.name)
        print("------")


def lst_room(room):
    players = ""
    for player in room.players:
        players += f"+{player.name}"
    return players[1::]


def update_players(room, other):
    roomLst = lst_room(room)
    for player in room.players:
        if other != player:
            player.conn.send("CNFM" + room.id + "+" + roomLst)
            print(f"[SERVER] Updated {player.name}")


def kick_players(room, id):
    for player in room.players:
        if player.name != id:
            player.conn.send("KICK")
            print(f"[SERVER] Kicked {player.name}")


def close_room(conn, addr, parms):
    _, roomid = parms
    room = rooms[roomid]
    if room:
        #verify player
        player = room.get_player(roomid)
        if player.addr != addr:
            return ("EROR", "EROR") 
        
        with mutex_lock:
            room = rooms.pop(roomid)
        if not room:
            print("failed")
            return ("EROR", "EROR")

        print_rooms()            
        kick_players(room, roomid)
        return ("CNFM", f"CNFM")

    print("failed")
    return ("EROR", "EROR")


def exit_room(conn, addr, parms):
    _, roomid, username = parms
    print(roomid)
    print(username)
    room = rooms[roomid]
    #verify player
    player = room.get_player(username)
    if player.addr != addr:
        return ("EROR", "EROR") 
    with mutex_lock:
        player = room.remove_player(username)
    print(player)
    if not player:
        print("failed")
        return ("EROR", "EROR")

    print_rooms()            
    update_players(room, player)
    return ("CNFM", f"CNFM")


def join_room(conn, addr, parms):
    _, roomId, username = parms
    global rooms
    try:
        room = rooms[roomId]
    except:
        print("failed")
        return ("EROR", "ERORRoom doesn't exist")
    player = Player(username, roomId, conn, addr)
    msg = room.add_player(player)
    if not msg:
        print("failed")
        return ("EROR", "ERORThere is already a player under this name in this room")
    
    print_rooms()
    update_players(room, player)
    return ("CNFM", f"CNFM{roomId}+{lst_room(room)}")
    

def create_room(conn, addr, parms):
    global rooms
    username = parms[1]
    if not (username in rooms.keys()):
        player = Player(username, username, conn, addr)
        room = Room(player)
        with mutex_lock:
            rooms[username] = room

        print(f"[SERVER] created room {username}")
        return ("CNFM", f"CNFM{username}+{username}")
    
    return ("EROR", "ERORThere is already a room under this name")


def handle_client(sock, addr):
    print(f"[SERVER] new connection from {addr}")
    conn = protocol.TCP(sock, HEADER)
    gameStart = False #only in the host thread
    username, roomid = None, None
    while not gameStart:
        try:
            request = conn.recv()
        except Exception as e:
            print(f"[SERVER] {addr} disconnected")
            print(f"[SERVER] checking for {username, roomid}")
            if not username or not roomid:
                return
            if username == roomid: #host -> close room
                print(f"[SERVER] host disconncted closed room {roomid}")
                close_room(conn, addr, (None, roomid))
            else:
                print(f"[SERVER] {username} disconncted from {roomid}")
                exit_room(conn, addr, (None, roomid, username))
            return
        request_code = request[:4]
        request_parms = request[4::].split("+")
        print(request)
        try:
            if request_code == "GSRT":
                break
                #end of thread, reopend thread in game_started
            msg = request_codes[request_code](conn, addr, request_parms)                
            if msg[0] == "CNFM":
                if request_code == "CRTR":
                    username = request_parms[1]
                    roomid = request_parms[1]
                elif request_code == "JOIN":
                    username = request_parms[2]
                    roomid = request_parms[1]
                elif request_code in ("EXIT", "CLSE"):
                    username, roomid = None, None
                conn.send(msg[1])
            elif msg[0] == "STRT":
                gameStart = True
            else:
                #error
                conn.send(msg[1])
        except Exception as e:
            pass
    
    if gameStart:
        game_started(conn, addr, msg[1])
    
        
def listen():
    print(f"[SERVER] listening on {ADDR}")
    main_server.listen(5)
    threads = []
    #change x later, len < x
    while len(threads) < 5:
        conn, addr = main_server.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()


def start_server():
    print(f"[SERVER] binded to {ADDR}")
    main_server.bind(ADDR)
    listen()


request_codes = {"CRTR" : create_room,
                 "JOIN": join_room,
                 "EXIT": exit_room,
                 "CLSE": close_room,
                 "STRT": start_game}


if __name__ == "__main__":
    start_server()
