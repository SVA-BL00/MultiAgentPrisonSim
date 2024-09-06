# start connection with client socket
# send and receive data from client
# close connection with client socket

import socket

# create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local machine name
host = "127.0.0.1"

port = 5000

# connection to hostname on the port
client_socket.connect((host, port))

# read jpg image
with open('../../assets/aerial-drone-pov.jpg', 'rb') as f:
    # bytes from image
    image_data = f.read()

    b = bytes(str(len(image_data)), 'ascii')

    # convert the image bytes to string
    client_socket.sendall(b)

    # write
    client_socket.sendall(image_data)
