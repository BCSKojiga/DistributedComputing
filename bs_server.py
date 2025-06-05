import socket
import threading

registered_nodes = []

def handle_client(conn, addr):
    global registered_nodes
    try:
        data = conn.recv(1024).decode()
        print("Received:", data.strip())

        tokens = data.split()
        length = tokens[0]
        command = tokens[1]

        if command == "REG":
            ip, port, name = tokens[2], tokens[3], tokens[4]

            # Check for duplicates
            for node in registered_nodes:
                if node[0] == ip and node[1] == port and node[2] == name:
                    conn.send(f"0055 REGOK 9998".encode())
                    conn.close()
                    return

            registered_nodes.append((ip, port, name))
            num = len(registered_nodes) - 1

            msg = f"REGOK {num}"
            for node in registered_nodes[:-1]:  # exclude current one
                msg += f" {node[0]} {node[1]} {node[2]}"
            msg = f"{len(msg)+5:04} {msg}"
            conn.send(msg.encode())

        elif command == "UNREG":
            ip, port, name = tokens[2], tokens[3], tokens[4]
            registered_nodes = [node for node in registered_nodes if not (node[0] == ip and node[1] == port and node[2] == name)]
            conn.send("0012 UNROK 0".encode())

        else:
            conn.send("9999".encode())

    except Exception as e:
        print("Error:", e)
        conn.send("9999".encode())

    finally:
        conn.close()

def start_bs_server():
    host = "127.0.0.1"
    port = 55555
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print("Bootstrap Server running on port", port)

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_bs_server()
