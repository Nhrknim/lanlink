import socket
import json
import time


DISCOVERY_PORT = 5556


def broadcast_room(room_name, host_name):

    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    message = {
        "room": room_name,
        "host": host_name
    }

    while True:
        udp.sendto(json.dumps(message).encode(), ("255.255.255.255", DISCOVERY_PORT))
        time.sleep(2)

def find_rooms():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    udp.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    udp.bind(("", DISCOVERY_PORT))
    udp.settimeout(0.5)

    rooms = {}
    start_time = time.time()

    while time.time() - start_time < 3:
        try:
            data, address = udp.recvfrom(1024)

            message = json.loads(data.decode())

            rooms[message["room"]] = {
                "host": message["host"],
                "ip": address[0]
            }

        except socket.timeout:
            continue

        except Exception as e:
            print("Discovery error:", e)

    udp.close()

    return rooms