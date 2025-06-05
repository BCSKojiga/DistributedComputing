import socket
from ttypes import Node
from random import shuffle

class BootstrapServerConnection:
    def __init__(self, bs, me):
        self.bs = bs
        self.me = me
        self.users = []

    def __enter__(self):
        self.users = self.connect_to_bs()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.unreg_from_bs()

    def message_with_length(self, message):
        '''
        Helper function to prepend the length of the message to the message itself
        Args:
            message (str): message to prepend the length
        Returns:
            bytes: Prepended message encoded as bytes
        '''
        message = " " + message
        message = str((10000+len(message)+5))[1:] + message
        return message.encode()  # <-- encode here to bytes

    def connect_to_bs(self):
        self.unreg_from_bs()
        buffer_size = 1024
        message = "REG "+ self.me.ip + " " +str(self.me.port) +" " + self.me.name

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.bs.ip, self.bs.port))
        s.send(self.message_with_length(message))  # now sending bytes
        data = s.recv(buffer_size)
        s.close()
        print(data)
        
        toks = data.decode().split()  # decode bytes to string before splitting
        
        if (len(toks) < 3):
            raise RuntimeError("Invalid message")
        
        if (toks[1] != "REGOK"):
            raise RuntimeError("Registration failed")
        
        num = int(toks[2])
        if (num < 0):
            raise RuntimeError("Registration failed")
            
        if (num == 0):
            return []
        elif (num == 1):
            return [Node(toks[3], int(toks[4]), toks[5])]
        else:
            l = list(range(1, num+1))
            shuffle(l)
            return [Node(toks[l[0]*3], int(toks[l[0]*3+1]), toks[l[0]*3+2]), 
                    Node(toks[l[1]*3], int(toks[l[1]*3+1]), toks[l[1]*3+2])]
        
    def unreg_from_bs(self):
        buffer_size = 1024
        message = "UNREG "+ self.me.ip + " " +str(self.me.port) +" " + self.me.name

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.bs.ip, self.bs.port))
        s.send(self.message_with_length(message))  # sending bytes
        data = s.recv(buffer_size)
        s.close()
        
        toks = data.decode().split()  # decode bytes to string before splitting
        if (toks[1] != "UNROK"):
            raise RuntimeError("Unreg failed")
