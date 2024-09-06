from ultralytics import YOLO
import socket
import logging
import cv2
import numpy as np
from threading import Thread, Event as ThreadEvent

from time import sleep

model = YOLO('yolov8s.pt')
#fps part
import time

from concurrent.futures import ThreadPoolExecutor

# Create a pool of threads (adjust the number of workers as needed)
executor = ThreadPoolExecutor(max_workers=5)

def clean_buffer(original_buffer):
    buffer = b''
    for b in original_buffer:
        if b == 255:
            break
        buffer += bytes([b])
    return buffer

def get_numeric_data(buffer):
    numeric_buffer = b''
    left_bytes = b''

    for b in buffer:
        if b >= 48 and b <= 57:
            numeric_buffer += bytes([b])
        else:
            left_bytes += bytes([b])

    return numeric_buffer, left_bytes

def handle_socket_client(client_socket, addr, port):
    logger = logging.getLogger("handle_socket_client")
    logger.info(f"connected to client: {addr} on port {port}")

    while True:
        data = client_socket.recv(7)
        if not data:
            break

        numeric_data, initial_buffer = get_numeric_data(data)
        data_len = int(numeric_data.decode('ascii'))
        logger.info("data_len: {}".format(data_len))

        buffer = initial_buffer
        bytes_left = data_len - len(buffer)

        while bytes_left > 0:
            fragment = client_socket.recv(bytes_left)
            if not fragment:
                break
            buffer += fragment
            bytes_left = data_len - len(buffer)

        if len(buffer) != data_len:
            logger.error("received data length does not match the expected length")
            break
        
        # Convert buffer to image
        nparr = np.frombuffer(buffer, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Submit the YOLO processing task to the thread pool
        future = executor.submit(process_image_with_yolo, img, port)

    client_socket.close()
    cv2.destroyAllWindows()
    logger.info("client disconnected")

def process_image_with_yolo(img, port):
    """Function to handle YOLO inference and image processing"""
    results = model.track(img, persist=True)
    
    # Check if any bunnies were detected
    bunnies = [r for r in results[0].boxes.cls if model.names[int(r)] == 'bunny']
    
    if bunnies:
        # Get the number of bunnies detected
        num_bunnies = len(bunnies)
        
        # Get the processing times
        preprocess_time = results[0].speed['preprocess']
        inference_time = results[0].speed['inference']
        postprocess_time = results[0].speed['postprocess']
        
        # Print the information
        print(f"Port {port}: {img.shape[1]}x{img.shape[0]} {num_bunnies} bunny, {inference_time:.1f}ms")
        print(f"Speed: {preprocess_time:.1f}ms preprocess, {inference_time:.1f}ms inference, {postprocess_time:.1f}ms postprocess per image at shape {img.shape}")
    
    annotated_frame = results[0].plot()

    # Display results
    cv2.imshow('YOLOv8 Tracking', annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return
exit_socket_server_flag = ThreadEvent()

def socket_server(port):
    logger = logging.getLogger(f"socket_server_{port}")

    HOST = '127.0.0.1'
    PORT = port  # Dynamically pass the port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    server_socket.settimeout(1)

    logger.info(f"Server listening on port: {HOST}:{PORT}")
    while not exit_socket_server_flag.is_set():
        try:
            client_socket, addr = server_socket.accept()
            Thread(target=handle_socket_client, args=(client_socket, addr, port)).start()
        except socket.timeout:
            continue

    logger.info(f"Terminating socket server on port {PORT}")
    server_socket.close()

# To run multiple servers on different ports
port_list = [5001, 5002, 5003, 5004, 5005]  # Add more ports if needed
server_threads = []

for port in port_list:
    server_thread = Thread(target=socket_server, args=(port,))
    server_threads.append(server_thread)
    server_thread.start()

# Wait for 'q' to stop
while True:
    if input("press 'q' to exit\n") == 'q':
        exit_socket_server_flag.set()
        break

# Join all threads
for server_thread in server_threads:
    server_thread.join()