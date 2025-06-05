class Node:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name

    def __repr__(self):
        return f"Node({self.ip}, {self.port}, {self.name})"
