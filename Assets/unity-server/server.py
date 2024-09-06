from ultralytics import YOLO
import socket
import logging
import cv2
import numpy as np
from threading import Thread, Event as ThreadEvent
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# YOLO model (you can use a lighter version like YOLOv8n for better performance)
model = YOLO('yolov8s.pt', verbose=False)

# Thread pool for image processing
executor = ThreadPoolExecutor(max_workers=3)

def handle_socket_client(client_socket, addr, port):
    logger.info(f"Connected to client: {addr} on port {port}")

    while True:
        try:
            # Receive the 7-byte header containing the image size
            data = client_socket.recv(7)
            if len(data) < 7:
                break

            # Get image data length
            data_len = int(data.decode('ascii'))
            buffer = b''
            while len(buffer) < data_len:
                buffer += client_socket.recv(data_len - len(buffer))

            if len(buffer) != data_len:
                logger.error("Received incomplete image data")
                break

            # Process the received image
            nparr = np.frombuffer(buffer, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Resize the image to reduce YOLO processing load
            img_resized = cv2.resize(img, (320, 320))  # Resize to 320x320 for faster inference
            executor.submit(process_image_with_yolo, img_resized, port)

        except Exception as e:
            logger.error(f"Error processing data from client: {e}")
            break

    client_socket.close()
    logger.info("Client disconnected")

def process_image_with_yolo(img, port):
    """Function to handle YOLO inference and image processing"""
    results = model.track(img, persist=True, verbose=False)

    # Check if any objects were detected
    detections = results[0].boxes
    bunnies = [r for r in detections if model.names[int(r.cls)] == 'bunny']
    
    # Send detection status back to Unity
    bunny_detected = bool(bunnies)
    send_detection_status(port, bunny_detected)
    
    if bunny_detected:
        logger.info(f"Port {port}: Bunny detected")
    else:
        pass
        #logger.info(f"Port {port}: No bunny detected")

def send_detection_status(port, status):
    """Send detection status (bool) back to Unity"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(str(int(status)).encode(), ('127.0.0.1', port))


def socket_server(port):
    HOST = '127.0.0.1'
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, port))
    server_socket.listen(5)

    logger.info(f"Server listening on port: {HOST}:{port}")
    while not exit_socket_server_flag.is_set():
        try:
            client_socket, addr = server_socket.accept()
            Thread(target=handle_socket_client, args=(client_socket, addr, port)).start()
        except socket.timeout:
            continue

    logger.info(f"Terminating socket server on port {port}")
    server_socket.close()

# Run multiple servers on different ports
port_list = [5001, 5002, 5003, 5004, 5005]
server_threads = []

exit_socket_server_flag = ThreadEvent()
for port in port_list:
    server_thread = Thread(target=socket_server, args=(port,))
    server_threads.append(server_thread)
    server_thread.start()

while True:
    if input("Press 'q' to exit\n") == 'q':
        exit_socket_server_flag.set()
        break

for server_thread in server_threads:
    server_thread.join()
