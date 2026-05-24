import socket
import threading

HOST = "0.0.0.0"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
server.settimeout(1)

clients = {}  # {socket: username}

print(f"Server running on port {PORT}")


def broadcast(message, sender=None):
    for client in list(clients.keys()):
        if client != sender:
            try:
                client.send(message.encode())
            except:
                if client in clients:
                    del clients[client]
                client.close()


def handle_client(client):
    username = clients[client]

    while True:
        try:
            message = client.recv(1024).decode()

            if not message:
                break

            full_message = f"{username}: {message}"

            print(full_message)

            broadcast(full_message, client)

        except Exception as e:
            print("Error:", e)
            break

    leave_message = f"*** {username} left the chat ***"

    print(leave_message)

    if client in clients:
        del clients[client]

    broadcast(leave_message)

    client.close()


try:
    while True:
        try:
            client_socket, client_address = server.accept()

            print(f"Connected: {client_address}")

            clients.append(client_socket)

            thread = threading.Thread(
                target=handle_client,
                args=(client_socket,)
            )
            thread.start()

        except socket.timeout:
            continue

except KeyboardInterrupt:
    print("\nServer shutting down...")

finally:
    server.close()
