from flask import Flask
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('drone_handler')
def handle_drone(message):
    try:
        data = json.loads(message)
        #print('Received environment data:', data)
        
        # TDO: Implement your agent logic here
        action = determine_action(data)
        
        emit('drone_response', {'command': action})
    except json.JSONDecodeError:
        print('Received invalid JSON:', message)
    except Exception as e:
        print(f"Error processing drone data: {str(e)}")

def determine_action(data):
    import random
    actions = ['move', 'turnN','turnS','turnW','turnE']
    #return random.choice(actions)
    return 'move'

if __name__ == '__main__':
    print("Starting WebSocket server...")
    socketio.run(app, debug=True, port=5000)