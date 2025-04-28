import pickle
""" requests - types
confirm - CNFM
create room - CRTR+username
join room - JOIN+roomid+username  --- roomid is the username of the host
exit room - EXIT+roomid+username
close room - CLSE+roomid
kick out of the room - KICK --- server kicks players becuase the host closed
start game - STRT+roomid
game started for player - GSRT
sentence send - SENT+sentence
"""
class TCP:
    def __init__(self, sock, header):
        self.format = "utf-8"
        self.__sock = sock
        self.__header = header
    

    def recv(self):
        header = int(self.__sock.recv(self.__header).decode(self.format)) #msg len
        request = self.__sock.recv(header).decode(self.format)
        return request
    

    def send(self, msg):
        header = str(len(msg))
        header = "0" * (self.__header - len(header)) + header
        request = header + msg
        print(request)
        self.__sock.send(request.encode(self.format))


    def confirm(self):
        self.send("CNFM")
    

    def timeout(self, sec):
        self.__sock.settimeout(sec)
    

    def sendall(self, bytes):
        length = str(len(bytes))
        self.send(length) #sending the length of image
        self.__sock.sendall(bytes) #send all the image
    

    def recvall(self):
        # Receive the first 4 bytes (image length)
        length_bytes = self.recv()
        try:
            img_length = int(length_bytes)
        except:
            return length_bytes
        # Receive the image data
        received_data = b''
        while len(received_data) < img_length:
            packet = self.__sock.recv(4096)
            if not packet:
                break
            received_data += packet
        
        return received_data
    

    def send_obj(self, obj):
        data = pickle.dumps(obj)
        print(data)
        self.__sock.sendall(data)
    

    def recv_obj(self):
        data = b""
        while True:
            print("recv")
            packet = self.__sock.recv(4096)
            if not packet:
                break
            data += packet

        return pickle.loads(data)