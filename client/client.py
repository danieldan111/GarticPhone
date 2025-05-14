import socket
import gui
import threading
import time
import protocol
import base64


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_addr = ("127.0.0.1", 6060)
sock.connect(server_addr)

conn = protocol.TCP(sock, 5)

global keepGoing
keepGoing = True

def checkQ():
    while keepGoing and screen.active:
        time.sleep(0.1) #adjust later
        if len(screen.requests_queue) > 0:
            request = screen.requests_queue.pop(0)
            # print(request) #skip
            # print(request)
            if request == "DISC":
                conn.send(request)
                print("ENDED")
                return
            if request[:3] == "IMG":
                conn.sendall(base64.b64decode(request[3::]))
                screen.answer = conn.recvall()
            elif request == "obj":
                print("recving obj")
                screen.answer = conn.recv_obj()
            elif request != "skip": 
                conn.send(request)
                msg = conn.recv()
                print(msg)
                screen.answer = msg     
            else: #skip send and go to recv
                conn.timeout(0.1)
                try:
                    msg = conn.recv()
                    print(msg)
                    screen.answer = msg          

                except socket.timeout:
                    pass
                
                conn.timeout(None)
            
        

screen = gui.GUI() 
t = threading.Thread(target=checkQ)
t.start()
screen.start()
print("closed")
t.join()
screen.destroy()
print("finished")
sock.close()

print("window closed, ended")
