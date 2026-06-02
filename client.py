import socket
import threading
import json

SERVER_IP = input("Enter server IP:")
USERNAME = input("Enter username:")

PORT = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))
buffer = ""

# ----------JSON HELPERS-----------


def send_json(data):

    message = json.dumps(data) + "\n"

    client.send(
        message.encode()
    )


def receive_json():

    global buffer


    while "\n" not in buffer:

        data = client.recv(1024).decode()


        if not data:
            return None


        buffer += data


    message, buffer = buffer.split(
        "\n",
        1
    )


    return json.loads(message)

# ---------------LOGIN-----------------


login_data = {
    "type": "login",
    "username": USERNAME
}

send_json(login_data)

# -----------RECEIVE THREAD------------


def receive_messages():
    while True:
        try:
            data = receive_json()

            if data is None:
                break

            if data["type"] == "chat":
                print(
                    f"{data['sender']} : {data['message']}"
                )
            elif data['type'] == "system":
                print(
                    f"*** {data['message']} ***"
                )
            elif data['type'] == "users":
                users = ", ".join(data["users"])
                print(f"Online users:{users}")
        except Exception as e:
            print("Connection closed")
            break

# start recieve thread


thread = threading.Thread(target=receive_messages, daemon=True)
thread.start()

# --------SEND LOOP-----

try:
    while True:

        message = input()

        data = {
            "type": "chat",
            "message": message
        }

        send_json(data)

except KeyboardInterrupt:

    print("\nDisconnected")

    client.close()
