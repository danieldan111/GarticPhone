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
        return self.__msgs


