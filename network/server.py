import socket
import threading
from network.protocol import send_json, receive_json



HOST = "0.0.0.0"
PORT = 5555


server=None


clients = {}   # {socket: username}
buffers = {}

running = True


def stop_server():

    global running

    running = False

    shutdown_message = {
        "type": "shutdown",
        "message": "Room closed by host"
    }

    broadcast(shutdown_message)

# ---------- BROADCAST MESSAGE ----------

def broadcast(message, sender=None):

    for client in list(clients.keys()):

        if client != sender:
            try:
                send_json(client, message)

            except:
                if client in buffers:
                    del buffers[client]

                client.close()


# ---------- ONLINE USERS ----------

def send_user_list():

    data = {
        "type": "users",
        "users": list(clients.values())
    }

    for client in list(clients.keys()):
        try:
            send_json(client, data)

        except:
            pass


# ---------- HANDLE EACH CLIENT ----------

def handle_client(client):

    username = clients[client]

    while True:
        try:
            data, buffers[client] = receive_json(client, buffers[client])

            if data is None:
                break

            if data["type"] == "chat":

                message = {
                    "type": "chat",
                    "sender": username,
                    "message": data["message"]
                }

                print(
                    f"{username}: {data['message']}"
                )

                broadcast(
                    message,
                    client
                )
            elif data["type"] == "private":

                private_message = {
                    "type": "private",
                    "sender": username,
                    "message": data["message"]
                }

                for user_socket, user_name in clients.items():

                    if user_name == data["to"]:

                        send_json(
                            user_socket,
                            private_message
                        )

                        break
            elif data["type"] == "file":

                # ---------- CREATE FILE HEADER ----------

                file_message = {
                    "type": "file",
                    "sender": username,
                    "filename": data["filename"],
                    "size": data["size"],
                    "private": bool(data.get("to"))
                }

                # ---------- FIND RECEIVERS ----------

                receivers = []

                # Private file transfer
                if data.get("to"):

                    for user_socket, user_name in clients.items():

                        if user_name == data["to"]:

                            receivers.append(user_socket)
                            break

                # Public file transfer
                else:

                    for user_socket in list(clients.keys()):

                        if user_socket != client:

                            receivers.append(user_socket)

                # ---------- SEND FILE HEADER ----------

                for receiver in receivers:

                    send_json(
                        receiver,
                        file_message
                    )

                # ---------- TRANSFER FILE DATA ----------

                remaining = data["size"]

                while remaining > 0:

                    chunk = client.recv(
                        min(
                            4096,
                            remaining
                        )
                    )

                    if not chunk:
                        break

                    remaining -= len(chunk)

                    for receiver in receivers:

                        receiver.send(
                            chunk
                        )

                print(
                    f"File transfer completed: {data['filename']}"
                )

        except Exception as e:
            print("Error:", e)
            break

    # Client disconnected

    if client in clients:
        del clients[client]

    leave_message = {
        "type": "system",
        "message": f"{username} left the chat"
    }

    print(leave_message["message"])

    broadcast(leave_message)

    send_user_list()

    client.close()


# ---------- SERVER LOOP ----------

def start_server():

    global server

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    server.settimeout(1)

    print(f"Server running on port {PORT}")

    try:

        while running:

            try:
                client_socket, client_address = server.accept()

                # Receive login details
                buffers[client_socket] = ""

                login_data, buffers[client_socket] = receive_json(
                    client_socket,
                    buffers[client_socket]
                )

                username = login_data["username"]

                clients[client_socket] = username

                print(f"{username} connected from {client_address}")


                join_message = {
                    "type": "system",
                    "message": f"{username} joined the chat"
                }

                broadcast(join_message)

                send_user_list()


                thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket,),
                    daemon=True
                )

                thread.start()


            except socket.timeout:
                continue


    except KeyboardInterrupt:
        print("\nServer shutting down...")


    finally:
        shutdown_message ={
            "type": "shutdown",
            "message": "Room closed by host"
        }
        broadcast(shutdown_message)

        for client in list(clients.keys()):
            client.close()

        server.close()


if __name__ == "__main__":
    start_server()