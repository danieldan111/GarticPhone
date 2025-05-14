import pickle
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
import base64
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
        self.secure()

    def secure(self):
        keySwitch = KeyExchange(self.__sock)
        self.__aes_key, self.__iv = keySwitch.switch_keys()
        del keySwitch


    def send(self, msg):
        # Encrypt the message using AES-CBC
        cipher = AES.new(self.__aes_key, AES.MODE_CBC, self.__iv)
        padded_msg = pad(msg.encode(self.format), AES.block_size)
        encrypted_msg = cipher.encrypt(padded_msg)

        # Create and send the header (length of the encrypted message)
        header = str(len(encrypted_msg)).zfill(self.__header)
        self.__sock.send(header.encode(self.format) + encrypted_msg)

    def recv(self):
        # Read the fixed-length header
        header_bytes = self.__sock.recv(self.__header)
        header = int(header_bytes.decode(self.format))

        # Read the encrypted message based on the header
        encrypted_msg = self.__sock.recv(header)

        # Decrypt the message using AES-CBC
        cipher = AES.new(self.__aes_key, AES.MODE_CBC, self.__iv)
        padded_msg = cipher.decrypt(encrypted_msg)
        msg = unpad(padded_msg, AES.block_size).decode(self.format)

        return msg



    def confirm(self):
        self.send("CNFM")
    

    def timeout(self, sec):
        self.__sock.settimeout(sec)
    

    def sendall(self, data: bytes):
        # Encrypt the data
        cipher = AES.new(self.__aes_key, AES.MODE_CBC, self.__iv)
        padded_data = pad(data, AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)

        # Send the encrypted length
        self.send(str(len(encrypted_data)))

        # Send the encrypted binary data
        self.__sock.sendall(encrypted_data)

    def recvall(self):
        # Receive and decrypt the encrypted length first
        length_str = self.recv()
        try:
            encrypted_length = int(length_str)
        except ValueError:
            return length_str  # Could be error or handshake message

        # Now receive the encrypted data
        received_data = b''
        while len(received_data) < encrypted_length:
            chunk = self.__sock.recv(4096)
            if not chunk:
                break
            received_data += chunk

        # Decrypt the full payload
        cipher = AES.new(self.__aes_key, AES.MODE_CBC, self.__iv)
        decrypted_padded = cipher.decrypt(received_data)
        decrypted = unpad(decrypted_padded, AES.block_size)

        return decrypted
    

    def send_obj(self, obj):
        # Serialize the object to bytes
        data = pickle.dumps(obj)

        # Encrypt the data
        cipher = AES.new(self.__aes_key, AES.MODE_CBC, self.__iv)
        padded_data = pad(data, AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)

        # Send the length of encrypted data first (AES encrypted)
        self.send(str(len(encrypted_data)))

        # Send the encrypted serialized object
        self.__sock.sendall(encrypted_data)

    def recv_obj(self):
        # First receive the encrypted length (as plaintext string)
        encrypted_length_str = self.recv()
        try:
            encrypted_length = int(encrypted_length_str)
        except ValueError:
            return encrypted_length_str  # Possibly a control message or error

        # Receive the full encrypted payload
        encrypted_data = b""
        while len(encrypted_data) < encrypted_length:
            packet = self.__sock.recv(4096)
            if not packet:
                break
            encrypted_data += packet

        # Decrypt the data
        cipher = AES.new(self.__aes_key, AES.MODE_CBC, self.__iv)
        decrypted_padded = cipher.decrypt(encrypted_data)
        decrypted_data = unpad(decrypted_padded, AES.block_size)

        # Deserialize the object
        return decrypted_data
    

#rsa
class KeyExchange:
    def __init__(self, sock):
        self.sock = sock


    def switch_keys(self):
        self.__private_key, self.__public_key = self.generate_rsa_keys()
        self.sock.send(self.__public_key)
        encrypted_aes_key = self.sock.recv(1024)
        iv = self.sock.recv(16)
        aes_key = self.decrypt_aes_key(encrypted_aes_key, self.__private_key)

        return (aes_key, iv)    


    def generate_rsa_keys(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key, public_key


    def decrypt_aes_key(self, encrypted_aes_key, private_key):
        private_rsa_key = RSA.import_key(private_key)
        cipher_rsa = PKCS1_OAEP.new(private_rsa_key)
        return cipher_rsa.decrypt(encrypted_aes_key)