from ultralytics import YOLO
import socket
import logging
import cv2
import numpy as np
from threading import Thread, Event as ThreadEvent
from time import sleep
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model = YOLO('yolov8s.pt', verbose= False)

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
    logger.info(f"Connected to client: {addr} on port {port}")

    while True:
        try:
            # First, check if we are handling status or image data
            # You could use a flag or a specific protocol to decide whether it's status or image data.
            # For simplicity, assume that if the client sends 7 bytes, it's an image; otherwise, it's status.

            # Try to receive the 7-byte length header
            data = client_socket.recv(7)

            # Check if the received data is less than 7 bytes (likely to be the detection status)
            if len(data) < 7:
                # Assume this is the detection status being sent (a single byte)
                if data:
                    status = data[0]
                    logger.info(f"Received detection status: {status}")
                    # Process the detection status here, e.g., log or notify
                break

            if not data:
                break

            # If 7 bytes received, assume it's image data
            numeric_data, initial_buffer = get_numeric_data(data)
            data_len = int(numeric_data.decode('ascii'))  # Expected length of image data

            buffer = initial_buffer
            bytes_left = data_len - len(buffer)

            # Log expected and actual received lengths for debugging
            logger.info(f"Expected data length: {data_len}, Initial buffer length: {len(initial_buffer)}")

            while bytes_left > 0:
                fragment = client_socket.recv(bytes_left)
                if not fragment:
                    logger.error("Incomplete data fragment received")
                    break
                buffer += fragment
                bytes_left = data_len - len(buffer)

            # Ensure the buffer size matches the expected data length
            if len(buffer) != data_len:
                logger.error(f"Received data length {len(buffer)} does not match the expected length {data_len}")
                break

            # Process the image
            nparr = np.frombuffer(buffer, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Submit the YOLO processing task
            executor.submit(process_image_with_yolo, img, port)

        except Exception as e:
            logger.error(f"Error while processing data from client: {e}")
            break

    client_socket.close()
    cv2.destroyAllWindows()
    logger.info("Client disconnected")


    client_socket.close()
    cv2.destroyAllWindows()
    logger.info("Client disconnected")


def process_image_with_yolo(img, port):
    """Function to handle YOLO inference and image processing"""
    from contextlib import redirect_stdout
    import io

    f = io.StringIO()
    with redirect_stdout(f):
        results = model.track(img, persist=True, verbose=False)

    # Check if any objects were detected
    detections = results[0].boxes
    if len(detections) == 0:
        send_detection_status(port, False)
        return  # No detections, exit silently
    # Filter for bunnies
    bunnies = [r for r in detections if model.names[int(r.cls)] == 'bunny']
    
    if bunnies:
        send_detection_status(port, True)
        # Get the number of bunnies detected
        num_bunnies = len(bunnies)
        
        # Get the processing times
        preprocess_time = results[0].speed['preprocess']
        inference_time = results[0].speed['inference']
        postprocess_time = results[0].speed['postprocess']
        
        # Print the information (only for bunny detections)
        print(f"Port {port}: {img.shape[1]}x{img.shape[0]} {num_bunnies} bunny, {inference_time:.1f}ms")
        print(f"Speed: {preprocess_time:.1f}ms preprocess, {inference_time:.1f}ms inference, {postprocess_time:.1f}ms postprocess per image at shape {img.shape}")

exit_socket_server_flag = ThreadEvent()

def send_detection_status(port, status):
    """Send detection status (True/False) back to the Unity client"""
    try:
        # Open a connection to send the status
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', port))
        
        # Send the actual byte (not the ASCII representation of '1' or '0')
        status_byte = bytes([1]) if status else bytes([0])

        # Log the status being sent for debugging
        logger.info(f"Sending detection status: {status_byte[0]} to port {port}")

        # Send the status byte
        client_socket.sendall(status_byte)

        # Ensure the socket stays open long enough for transmission
        client_socket.shutdown(socket.SHUT_WR)
        client_socket.close()
    except Exception as e:
        logger.error(f"Failed to send detection status to Unity: {e}")




def socket_server(port):
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
    if input("Press 'q' to exit\n") == 'q':
        exit_socket_server_flag.set()
        break

# Join all threads
for server_thread in server_threads:
    server_thread.join()