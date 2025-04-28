""""
if someone leaves midgame he will send nothing each round
"""


class Room:
    def __init__(self, player):
        self.__id = player.name
        self.__players = []
        self.__players.append(player)
    

    def add_player(self, player):
        for other in self.__players:
            if other.name == player.name:
                #error
                return 
        
        self.__players.append(player)
        return "CNFM"


    def remove_player(self, username):
        for i in range(len(self.__players)):
            if username == self.__players[i].name:
                #remove
                player = self.__players.pop(i)
                return player


    def get_player(self, username):
        for i in range(len(self.__players)):
            if username == self.__players[i].name:
                player = self.__players[i]
                return player


    @property
    def id(self):
        return self.__id
    

    @property
    def players(self):
        return self.__players


class Player:
    def __init__(self, name, roomid, conn, addr):
        self.__name = name
        self.__id = roomid
        self.conn = conn
        self.addr = addr
    

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__id
    
