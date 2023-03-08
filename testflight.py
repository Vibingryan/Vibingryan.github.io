import socket
import threading
import time
import random

# IP and port of Tello drones
tello_addresses = [('192.168.0.100', 8889), ('192.168.0.103', 8889), ('192.168.0.105', 8889), ('192.168.0.106', 8889)]

# IP and port of local computer
local_address = ('', 9010)

# Create UDP connections for each Tello drone
socks = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in range(4)]

# Bind to the local address and port for each Tello drone
for i, sock in enumerate(socks):
    sock.bind((local_address[0], local_address[1] + i))


# Send the message to Tello and allow for a delay in seconds
def send(sock, address, message, delay=0):
    try:
        sock.sendto(message.encode(), address)
        print(f"Sending message to {address}: {message}")
    except Exception as e:
        print(f"Error sending to {address}: {str(e)}")

    time.sleep(delay)


# Receive the message from Tello
def receive(sock, id):
    while True:
        try:
            response, ip_address = sock.recvfrom(128)
            print(f"Received message from Tello {id}: {response.decode(encoding='utf-8')}")
        except Exception as e:
            print(f"Error receiving from Tello {id}: {str(e)}")
            break


# Create and start a receiving thread for each Tello drone
receive_threads = [threading.Thread(target=receive, args=(socks[i], i + 1)) for i in range(4)]
for thread in receive_threads:
    thread.daemon = True
    thread.start()

# Delay for initial setup
time.sleep(1)

# Put Tello drones into command mode
for i, address in enumerate(tello_addresses):
    send(socks[i], address, "command")

# Delay for command mode
time.sleep(1)

# Send takeoff command to each Tello drone and wait for takeoff to complete
for i, address in enumerate(tello_addresses):
    send(socks[i], address, "takeoff", 5)

# Set box leg distance
box_leg_distance = 100
altitude = 50

# Loop and create each leg of the box for each Tello drone
for i, address in enumerate(tello_addresses):
    send(socks[i], address, f"forward {box_leg_distance}")
    send(socks[i], address, "flip l")
    send(socks[i], address, f"forward {box_leg_distance}")
    send(socks[i], address, "flip r")
    send(socks[i], address, f"back {box_leg_distance}")
    send(socks[i], address, "flip l")
    send(socks[i], address, f"back {box_leg_distance}")
    send(socks[i], address, "flip r")

# Set rotation angle and direction
rotation_angle = 180
rotation_directions = ['cw', 'ccw']

# Loop and perform rotation for each Tello drone
for i, address in enumerate(tello_addresses):
    send(socks[i], address, f"{rotation_directions[i % 2]} {rotation_angle}")

# Loop that would adjust altitude before moving randomly
for i, address in enumerate(tello_addresses):
    send(socks[i], address, f"up {altitude - 50}")
    send(socks[i], address, f"up {altitude}")
    send(socks[i], address, f"up {altitude + 50}")
    send(socks[i], address, f"up {altitude + 100}")

# Move each Tello drone randomly
for i, address in enumerate(tello_addresses):
    send(socks[i], address, f"right {random.randint(50, 150)}")
    send(socks[i], address, f"left {random.randint(50, 150)}")
    send(socks[i], address, f"forward {random.randint(50, 150)}")
    send(socks[i], address, f"back {random.randint(50, 150)}")

for i, address in enumerate(tello_addresses):
    send(socks[i], address, f"land {random.randint(50, 150)}")
    send(socks[i], address, f"land {random.randint(50, 150)}")
    send(socks[i], address, f"land {random.randint(50, 150)}")
    send(socks[i], address, f"land {random.randint(50, 150)}")

socks.close()
