import socket
import threading

SERVER_IP = input("Enter server IP: ")
PORT = 5555

username = input("Enter username: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((SERVER_IP, PORT))

client.send(username.encode())

print("Connected!")


def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode()

            if not message:
                break

            print(f"\n{message}")

        except:
            break


threading.Thread(
    target=receive_messages,
    daemon=True
).start()


while True:
    message = input()

    if message.lower() == "exit":
        break

    client.send(message.encode())

client.close()