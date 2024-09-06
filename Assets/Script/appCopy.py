from flask import Flask, request
from flask_socketio import SocketIO, emit
import json
import agentpy as ap
from owlready2 import *
import ast


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize ontology
onto = get_ontology("file://onto.owl")

#ONTOLOGIA
#onto.delete()
with onto:
    class Entity(Thing):
        pass

    class Drone(Entity):
        pass

    class Place(Thing):
        pass

    class Position(Thing):
        pass

    class Prisioner(Entity):
        pass

    class Camera(Entity):
        pass

    class Security(Entity):
        pass

    class has_place(ObjectProperty, FunctionalProperty):
        domain = [Entity]
        range = [Place]
        pass

    class has_position(DataProperty, FunctionalProperty):
        domain = [Place]
        range = [str]
        pass

    class has_existence(DataProperty, FunctionalProperty):
        domain = [Prisioner]
        range = [bool]
        pass

    class has_alert(DataProperty, FunctionalProperty):
        domain = [Camera]
        range = [bool]
        pass


class DroneAgent(ap.Agent):
    def see(self, e):
        """
        Perceive the environment
        """
        own_position = str(e.positions[self])
        self.per = [Drone(has_place=Place(has_position=str(own_position)))]

        computer_vision = ["building", "duck", "nbunny"]
        self.per.append(Prisioner(has_existence="bunny" in computer_vision))
        
        cameras_alert = [None, None, None, None]
        self.per.append(cameras_alert)

    def brf(self):
        """
        Modify beliefs based on perceptions and current beliefs
        """
        camera_names = ['camera1', 'camera2', 'camera3', 'camera4']
        self.beliefs['own_position'] = self.per[0]
        self.beliefs['seeing_prisioner'] = self.per[1]

        for i, alert in enumerate(self.per[2]):
          if i < len(camera_names):
              camera_name = camera_names[i]
              if camera_name in self.beliefs['cameras']:
                  if alert is None:
                      self.beliefs['cameras'][camera_name].has_alert = False
                  else:
                      self.beliefs['cameras'][camera_name].has_alert = True
        pass

    def opt(self):
        """
        Define a new goal based on current intentions and perception
        """
        pass

    def filter(self):
        """
        Choose a new intention based on beliefs, desires, and intentions
        """
        if self.first_step:
            self.intention = self.desires['path1'][1]
            self.beliefs['current_path'] = 'path1'

        for rule in self.rules:
            act = rule()
            if act is not None:
                act()
        

    def planning(self):
        """
        Define a plan given an intention and a set of actions
        """
        self.plan = self.find_path()

    def next(self):
        """
        Call the agent's reasoning and actions
        """
        self.brf()
        self.opt()
        self.filter()

        if self.first_step:
            self.planning()
            self.first_step = False
        elif self.beliefs['seeing_prisioner'].has_existence:
            self.alert()
        elif not self.plan:
            self.planning()
        elif self.plan:
            eval(self.plan[0])
            self.plan.pop(0)

    def setup(self):
        """
        Agent initialization
        """
        self.agentType = 0
        self.directionTag = 'N'
        self.direction = (-1, 0)
        self.per = []
        self.index = 0

        self.map = {}
        self.coordinates = {
            'camera1': (-61, 48),
            'camera2': (61, 48),
            'camera3': (61, -71),
            'camera4': (-61, -71)
        }

        for name, position in self.coordinates.items():
            camera = Camera(name)
            camera.has_place = Place(has_position=str(position))
            camera.has_alert = False
            self.map[name] = camera

        self.beliefs = {'own_position': None, 'seeing_prisioner': False, 'current_path': None, 'cameras': self.map}
        self.actions = (self.find_path, self.next_position, self.switch_path, self.move, self.turn, self.idle)
        self.rules = (self.rule_1, self.rule_2, self.rule_3, self.rule_4)
        self.desires = {
            'path1': [(4, 74), (-61, 48), (61, 48), (61, -71), (-61, -71)],
            'path2': [(4, 74), (4, 1), (-12, 1.5), (-12, 74)]
        }
        self.intention = None
        self.plan = None
        self.first_step = True

    def step(self, env):
        """
        Step function
        """
        self.see(env)
        self.next()
    
    def update(self):
      pass

    def end(self):
      pass

    def rule_1(self):
        """
        Deductive rule to choose the next intention
        """
        validator = [False, False, False, False]
        if self.beliefs['current_path'] == 'path1':
            validator[0] = True
        if self.per[0].has_place.has_position == str(self.intention):
            validator[1] = True
        if self.per[0].has_place.has_position != str(self.desires['path1'][-1]):
            validator[2] = True
        validator[3] = True
        for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
                validator[3] = False

        if sum(validator) == 4:
            return self.next_position

        return None

    def rule_2(self):
        """
        Deductive rule to switch paths
        """
        # Validador de regla
        validator = [False, False, False, False]

        # Proposición 1: Si estoy en path_1
        if self.beliefs['current_path'] == 'path1':
                validator[0] = True

        # Proposición 2: Si llegué a mi posición deseada
        if self.per[0].has_place.has_position == str(self.intention):
            validator[1] = True

        # Proposición 3: LLegué al final del camino
        if self.per[0].has_place.has_position == str(self.desires['path1'][-1]):
            validator[2] = True

        # Proposición 4: No hay alerta
        validator[3] = True
        for name, camera in self.beliefs['cameras'].items():
                if camera.has_alert == True:
                    validator[3] = False

        if sum(validator) == 4:
            return self.switch_path

        return None

    def rule_3(self):
        """
        Deductive rule for the next intention for path2
        """
        # Validador de regla
        validator = [False, False, False, False]

        # Proposición 1: Si estoy en path_2
        if self.beliefs['current_path'] == 'path2':
                validator[0] = True

        # Proposición 2: Si llegué a mi posición deseada
        if self.per[0].has_place.has_position == str(self.intention):
            validator[1] = True

        # Proposición 3: No he llegado al final del camino
        if self.per[0].has_place.has_position != str(self.desires['path2'][-1]):
            validator[2] = True

        # Proposición 4: No hay alerta
        validator[3] = True
        for name, camera in self.beliefs['cameras'].items():
                if camera.has_alert == True:
                    validator[3] = False

        if sum(validator) == 4:
            return self.next_position

        return None
    
    def rule_4(self):
        """
        Deductive rule to switch paths for path2
        """
        # Validador de regla
        validator = [False, False, False, False]

        # Proposición 1: Si estoy en path_2
        if self.beliefs['current_path'] == 'path2':
                validator[0] = True

        # Proposición 2: Si llegué a mi posición deseada
        if self.per[0].has_place.has_position == str(self.intention):
            validator[1] = True

        # Proposición 3: LLegué al final del camino
        if self.per[0].has_place.has_position == str(self.desires['path2'][-1]):
            validator[2] = True

        # Proposición 4: No hay alerta
        validator[3] = True
        for name, camera in self.beliefs['cameras'].items():
                if camera.has_alert == True:
                    validator[3] = False

        if sum(validator) == 4:
            return self.switch_path

        return None

    def find_path(self):
        path = []
        distance = tuple(int(a) - int(b) for a, b in zip( self.intention, self.model.grid.positions[self]))

        # Horizontal movement
        x = int(distance[0])
        path.append( self.turn('x', x) )
        for i in range(0, abs(x)):
          path.append('self.move()')

        # Vertical movement
        y = int(distance[1])
        path.append( self.turn('y', y) )
        for i in range(0, abs(y)):
          path.append('self.move()')

        return path

    def next_position(self):
        print(self.index)
        self.index += 1
        self.intention = self.desires[self.beliefs['current_path']][self.index]

    def switch_path(self):
        self.index = 0
        if self.beliefs['current_path'] == 'path1':
            self.beliefs['current_path'] = 'path2'
        elif self.beliefs['current_path'] == 'path2':
            self.beliefs['current_path'] = 'path1'
        self.intention = self.desires[self.beliefs['current_path']][self.index]


    def alert(self):
        self.plan = None
        self.intention = None
        self.idle()
        print("Communication with security agent")

    def move(self):
        if self.directionTag == 'N':
            self.model.grid.move_by(self, (-1, 0))
        if self.directionTag == 'S':
            self.model.grid.move_by(self, (1, 0))
        if self.directionTag == 'E':
            self.model.grid.move_by(self, (0, 1))
        if self.directionTag == 'W':
            self.model.grid.move_by(self, (0, -1))
        print(f"Moved to new position: {self.model.grid.positions[self]}")
        pass

    def turn(self, axis, distance):
        if axis == 'y' and distance < 0:
            return 'self.turnW()'
        elif axis == 'y' and distance > 0:
            return 'self.turnE()'
        elif axis == 'x' and distance < 0:
            return 'self.turnN()'
        elif axis == 'x' and distance > 0:
            return 'self.turnS()'
        else:
            return 'self.idle()'

    def turnN(self):
        self.direction = (-1,0) #Hacia Norte
        self.directionTag = "N"
        pass

    def turnS(self):
        self.direction = (1,0)  #Hacia Sur
        self.directionTag = "S"
        pass

    def turnE(self):
        self.direction = (0,1) #Hacia Este
        self.directionTag = "E"
        pass

    def turnW(self):
        self.direction = (0,-1) #Hacia Oeste
        self.directionTag = "W"
        pass

    def idle(self):
        pass


class PrisonModel(ap.Model):
    def setup(self):
        self.drones = ap.AgentList(self, self.p.drones, DroneAgent)
        self.grid = ap.Grid(self, (self.p.M, self.p.N), track_empty=True)
        self.grid.add_agents(self.drones, positions=(self.p.dpos), random=False, empty=True)

    def step(self):
        self.drones.step(self.grid)


@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def clean_action(action_str):
    # Remove "self." prefix and "()" suffix
    if action_str.startswith('self.') and action_str.endswith('()'):
        return action_str[5:-2]
    return action_str

@socketio.on('drone_handler')
def handle_drone(message):
    try:
        data = json.loads(message)
        
        # Initialize model with the received parameters
        parameters = {
            'drones': 1,
            'buildings': 0,
            'M': 200,
            'N': 200,
            'dpos': [(4,74)]
        }
        
        model = PrisonModel(parameters)
        model.run(steps=1)  # Ensure to run only one step at a time or as needed
        if model.drones and model.drones[0].plan:
            raw_action = model.drones[0].plan[0]
            action = clean_action(raw_action)
        else:
            action = 'idle'
        print(action)
        emit('drone_response', {'command': action})
    except json.JSONDecodeError:
        print('Received invalid JSON:', message)
    except Exception as e:
        print(f"Error processing drone data: {str(e)}")


if __name__ == '__main__':
    print("Starting WebSocket server...")
    socketio.run(app, debug=True, port=5000)