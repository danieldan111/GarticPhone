import time
import json
import os
import random


"""
game start: shuffle players list
ask for input from every player
"""

class Chat:
    def __init__(self, player):
        self.__msgs = []
        self.__host = player


    def addSentence(self, sentence):
        #sentences (player, msg)
        self.__msgs.append(sentence)
    

    def addImage(self, image):
        self.__msgs.append(image)
    

    def display(self):
        print(f"{self.__host}'s chat")
        for msg in self.__msgs:
            print(msg)
        print("--------")


    @property
    def name(self):
        return self.__host


    @property
    def chat(self):
        return (self.__host.name, self.__msgs)


class Game:
    def __init__(self, players):
        self.__players = players
        self.__rounds = len(players) * 2
        self.__currentRound = 0
        self.going = True
        self.close = False


    def random_rotate(self):
        rotated_players = self.__players
        rotations = random.randint(1, len(self.__players) - 1)
        for i in range(rotations):
            rotated_players = rotated_players[-1::] + rotated_players[:-1]
        return rotated_players


    def start(self):
        self.__chats = []
        for player in self.__players:
            self.__chats.append(Chat(player))

        #shuffle players list
        shuffled = self.random_rotate()
        self.__transport = {}
        for i in range(len(self.__players)):
            self.__transport[self.__players[i]] = shuffled[i]

        # print(self.__transport) 

        baseDir = os.path.dirname(os.path.abspath(__file__))
        jsonPath = os.path.join(baseDir, "gartic_phone_first_sentences.json")
        with open(jsonPath, "r") as file:
            sentences = json.load(file)

        
        random.shuffle(sentences)
        suggestions = random.sample(sentences, len(self.__players))
        # print(suggestions)

        #send suggestions
        return suggestions


    def currentTrans(self, player):
        current = player
        for i in range(self.__currentRound - 1):
            current = self.__transport[current]
        return current


    def sentences(self, sentences):
        #sentecnes is a dic player:sentence
        #transportation di - p1:p3, p3:p2, p2:p1
        self.__currentRound = self.__currentRound + 1

        for chat in self.__chats:
            chat.addSentence(sentences[self.currentTrans(chat.name)])
        #return val[0] == If the game continoues or not
        return (True,self.__transport, sentences)


    def images(self, images):
        #images is a dic- player:image
        self.__currentRound = self.__currentRound + 1

        for chat in self.__chats:
            chat.addSentence(images[self.currentTrans(chat.name)])
        if self.__currentRound == self.__rounds:
            # for chat in self.__chats:
            #     chat.display()
            self.going = False
            return (False,)

        return (True,self.__transport, images)
    

    @property
    def chats(self):
        return self.__chats

    @property
    def rounds(self):
        return self.__rounds


    @property
    def players(self):
        return self.__players
    

if __name__ == "__main__":
    players = [1, 2, 3, 4, 5]
    game = Game(players)
    game.start()

    sentences = {1:1, 2:2, 3:3, 4:4, 5:5}
    game.sentences(sentences)
    gameIsGoing = game.images(sentences)
    while gameIsGoing:
        game.sentences(sentences)
        gameIsGoing = game.images(sentences)

