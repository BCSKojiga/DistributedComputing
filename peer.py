import socket
import random
import threading
from ttypes import Node
from bootstrap_connection import BootstrapServerConnection

# Load files from master list
with open("files.txt") as f:
    all_files = [line.strip() for line in f.readlines()]

def udp_server(my_port, routing_table):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", my_port))
    print(f"[UDP] Listening on {my_port}")

    while True:
        data, addr = s.recvfrom(1024)
        msg = data.decode()
        print(f"[UDP] {msg} from {addr}")

        if "JOIN" in msg:
            tokens = msg.split()
            sender_ip = tokens[1]
            sender_port = int(tokens[2])
            # Update routing table if not already present
            if (sender_ip, sender_port) not in routing_table:
                routing_table.append((sender_ip, sender_port))
                print("[UDP] Routing table updated:", routing_table)

def start_node(port, name):
    print(f"Starting node '{name}' on port {port}...")  # Debug print
    me = Node("127.0.0.1", port, name)
    bs = Node("127.0.0.1", 55555, "BS")

    with BootstrapServerConnection(bs, me) as connection:
        peers = connection.users
        print(f"[{name}] Connected peers from BS:", peers)

        # Assign 3–5 random files to this node
        my_files = random.sample(all_files, random.randint(3, 5))
        print(f"[{name}] My files:", my_files)

        routing_table = []
        # Start UDP listener in a thread
        threading.Thread(target=udp_server, args=(port, routing_table), daemon=True).start()

        # Send JOIN messages to 2 random peers from BS list
        if peers:
            selected = random.sample(peers, min(2, len(peers)))
            for peer in selected:
                msg = f"JOIN {me.ip} {me.port}"
                msg = f"{len(msg)+5:04} {msg}"
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(msg.encode(), (peer.ip, peer.port))
                print(f"[{name}] Sent JOIN to {peer.ip}:{peer.port}")

        # Keep node alive and interactive
        while True:
            cmd = input(f"[{name}] > ").strip()
            if cmd == "files":
                print(f"[{name}] Files:", my_files)
            elif cmd == "table":
                print(f"[{name}] Routing Table:", routing_table)
            elif cmd == "exit":
                print(f"[{name}] Exiting...")
                break
            else:
                print("Commands: files, table, exit")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python peer.py <port> <name>")
    else:
        port = int(sys.argv[1])
        name = sys.argv[2]
        start_node(port, name)
