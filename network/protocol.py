import json


def send_json(socket, data):
    message = json.dumps(data) + "\n"
    socket.send(message.encode())


def receive_json(socket, buffer):

    while "\n" not in buffer:

        data = socket.recv(1024).decode()

        if not data:
            return None, buffer

        buffer += data


    message, buffer = buffer.split("\n", 1)

    return json.loads(message), buffer