from flask import Flask, request
from flask_socketio import SocketIO, emit
import json
import agentpy as ap
import ast
import networkx as nx
from matplotlib import pyplot as plt
from owlready2 import *
from collections import deque
import IPython
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def create_resource_if_not_exists(resource_class, resource_name):
    existing_resources = list(onto.search_one(iri=f"*{resource_name}"))
    if existing_resources:
        return existing_resources[0]
    return resource_class(resource_name)

# Initialize ontology
onto = get_ontology("file://onto.owl")
onto.load()
onto.destroy()
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


''' Message Class'''
class Message:
    performatives = ["take-control", "reply", "alert", "move-forward", "move-down", "capture"]

    def __init__(self, performative="", content="pass", sender=None, receiver=None):
        self.performative = performative if performative in self.performatives else ""
        self.content = content
        self.sender = sender
        self.receiver = receiver

    def print_message(msg):
        print("----")
        print(f"Performative: {msg.performative}")
        print(f"Content: {msg.content}")
        print(f"Sender: Agent {msg.sender}")
        print(f"Receiver: Agent {msg.receiver}")
        print("----")


""" Dron """
## Drone Agent Logic
class DroneAgent(ap.Agent):
    def see(self, e):
        """
        Perceive the environment
        """
        own_position = str(e.positions[self])
        self.per = [Drone(has_place=Place(has_position=str(own_position)))]

        computer_vision = ["building", "duck"]
        if "Prision" in computer_vision:
            self.per.append(Prisioner(has_existence = True))
        else:
            self.per.append(Prisioner(has_existence = False))
        
        cameras_alert = [self.model.dron.cam]
        print(cameras_alert)
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
        self.beliefs['camera_alert'] = self.choose_camera()
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
        print("FILTER")
        if self.first_step:
            self.intention = self.desires['path1'][1]
            self.beliefs['current_path'] = 'path1'

        for rule in self.rules:
            act = rule()
            print("ACT-")
            print(act)
            if act is not None:
                print("NOTNULL-")
                act()
        

    def planning(self):
        """
        Define a plan given an intention and a set of actions
        """
        self.plan = self.find_path()
        print("FUNCTION Planning")

    def next(self):
        """
        Call the agent's reasoning and actions
        """
        self.brf()
        self.opt()
        self.filter()

        if self.first_step:
            print("FIRST-planning")
            self.planning()
            self.first_step = False
        elif self.beliefs['seeing_prisioner'].has_existence:
            self.alert()
        elif not self.plan:
            print("NEXT-planning")
            self.planning()
        elif self.plan:
            self.actionU = self.plan[0]
            eval(self.plan[0])
            self.plan.pop(0)
        

    def setup(self):
        """
        Agent initialization
        """
        self.agentType = 0
        self.directionTag = 'N'
        self.direction = (0,1)
        self.per = []
        self.index = 0

        self.map = {}
        self.coordinates = {
            'camera1': (0, 119),
            'camera2': (122, 119),
            'camera3': (122, 0),
            'camera4': (0, 0)
        }

        for name, position in self.coordinates.items():
            camera = Camera(name)
            camera.has_place = Place(has_position=str(position))
            camera.has_alert = False
            self.map[name] = camera

        self.beliefs = {'own_position': None, 'seeing_prisioner': False, 'current_path': None, 'cameras': self.map}
        self.actions = (self.find_path, self.next_position, self.switch_path, self.move, self.turn, self.idle)
        #Reglas del agente
        self.rules = (
            self.rule_1,
            self.rule_2,
            self.rule_3,
            self.rule_4,
            self.rule_5,
            self.rule_6,
            self.rule_7,
            self.rule_8,
            self.rule_9,
            self.rule_10,
            self.rule_11,
            self.rule_12,
            self.rule_13,
            self.rule_14,
            self.rule_15,
            self.rule_16,
            self.rule_17,
            self.rule_18,
            self.rule_19
        )
      
        self.desires = {
            'path1': [(50, 0), (0, 0), (0, 119), (122, 119), (122, 0)],
            'path2': [(50, 0), (50, 40), (67, 40), (67, 0)]
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
            print("VALIDATOR1")
        if self.per[0].has_place.has_position == str(self.intention):
            validator[1] = True
            print("VALIDATOR2")
        if self.per[0].has_place.has_position != str(self.desires['path1'][-1]):
            validator[2] = True
            print("VALIDATOR3")
        validator[3] = True
        for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
                validator[3] = False
                print("VALIDATOR4")

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
    
    
    def rule_5(self):
      """
      Regla deductiva para ir a la cámara
      """

      #Validador de regla
      validator = [False, False, False]

      # Proposición 1: Si estoy en pos2
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path2'][1]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      #Ir a posición 1
      if sum(validator) == 3:
        self.intention = self.desires['path2'][0]

      return None

    #Estoy en pos 3, hay alerta, no veo nada con visión computacional -> Ir a pos4
    def rule_6(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False]

      # Proposición 1: Si estoy en pos3
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path2'][2]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      #Ir a posición 4
      if sum(validator) == 3:
        print("Intention changed")
        self.intention = self.desires['path2'][3]

      return None

    #Estoy en pos 4, hay alerta, no veo nada con visión computacional, cámara está a la derecha mía -> cambiar a path 1, ir a C4
    def rule_7(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False, False]

      # Proposición 1: Si estoy en pos4
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path2'][3]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      # Proposición 4: Cámara está a la derecha mía
      if self.beliefs['cameras']['camera3'].has_alert == True or self.beliefs['cameras']['camera4'].has_alert == True:
        validator[3] = True

      if sum(validator) == 4:
        print("Intention changed C4 :0")
        self.intention = self.desires['path1'][4]
        self.beliefs['current_path'] = 'path1'

      return None

    #Estoy en pos 4, hay alerta, no veo nada con visión computacional, cámara está a la izquierda mía -> cambiar a path 1, ir a C1
    def rule_8(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False, False]

      # Proposición 1: Si estoy en pos4
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path2'][3]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      # Proposición 4: Cámara está a la izquierda
      if self.beliefs['cameras']['camera1'].has_alert == True or self.beliefs['cameras']['camera2'].has_alert == True:
        validator[3] = True

      if sum(validator) == 4:
        print("Intention changed")
        self.intention = self.desires['path1'][1]
        self.beliefs['current_path'] = 'path1'

      return None

    #Estoy en pos 1, hay alerta, no veo nada con visión computacional, cámara está a la derecha -> cambiar a path 1, a C4
    def rule_9(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False, False]

      # Proposición 1: Si estoy en pos1
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path2'][0]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      # Proposición 4: Cámara está a la derecha
      if self.beliefs['cameras']['camera3'].has_alert == True or self.beliefs['cameras']['camera4'].has_alert == True:
        validator[3] = True

      if sum(validator) == 4:
        print("Intention changed")
        self.intention = self.desires['path1'][4]
        self.beliefs['current_path'] = 'path1'

      return None

    #Estoy en pos 1, hay alerta, no estoy en la posición de la cámara que mandó la alerta, no veo nada con visión computacional, cámara está a la izquierda mía -> cambiar a path 1, a C1
    def rule_10(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False, False]

      # Proposición 1: Si estoy en pos1
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path2'][0]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      # Proposición 4: Cámara está a la izquierda
      if self.beliefs['cameras']['camera1'].has_alert == True or self.beliefs['cameras']['camera2'].has_alert == True:
        validator[3] = True

      if sum(validator) == 4:
        print("Intention changed")
        self.intention = self.desires['path1'][1]
        self.beliefs['current_path'] = 'path1'

      return None


    #Estoy en pos C1, hay alerta, no estoy en la posición de la cámara que mandó la alerta, no veo nada con visión computacional, cámara está a la derecha mía -> dejar en path 1, ir a C4
    def rule_11(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False, False, False]

      # Proposición 1: Si estoy en C1
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path1'][1]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      # Proposición 4: Cámara está a la derecha
      if self.beliefs['cameras']['camera4'].has_alert == True:
        validator[3] = True

      # Proposición 5: No estoy en la posición de la cámara que envió la alerta
      if self.beliefs['own_position'].has_place.has_position != str(self.beliefs['camera_alert']):
        validator[4] = True

      if sum(validator) == 5:
        print("Intention changed")
        self.intention = self.desires['path1'][4]

      return None

    #Estoy en pos C1, hay alerta, no estoy en la posición de la cámara que mandó la alerta, no veo nada con visión computacional, cámara está arriba mío o cámara es C3 -> dejar en path 1, ir a C2
    def rule_12(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False, False, False]

      # Proposición 1: Si estoy en C1
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path1'][1]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      # Proposición 4: Cámara está arriba
      if self.beliefs['cameras']['camera2'].has_alert == True or self.beliefs['cameras']['camera3'].has_alert == True:
        validator[3] = True

      # Proposición 5: No estoy en la posición de la cámara que envió la alerta
      if self.beliefs['own_position'].has_place.has_position != str(self.beliefs['camera_alert']):
        validator[4] = True

      if sum(validator) == 5:
        print("Intention changed")
        self.intention = self.desires['path1'][2]

      return None


    #Estoy en pos C4, hay alerta, no estoy en la posición de la cámara que mandó la alerta, no veo nada con visión computacional, cámara está a la izquierda mía -> dejar en path 1, ir a C1
    def rule_13(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False, False, False]

      # Proposición 1: Si estoy en C4
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path1'][4]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      # Proposición 4: Cámara está a la izquierda
      if self.beliefs['cameras']['camera1'].has_alert == True:
        validator[3] = True

      # Proposición 5: No estoy en la posición de la cámara que envió la alerta
      if self.beliefs['own_position'].has_place.has_position != str(self.beliefs['camera_alert']):
        validator[4] = True

      if sum(validator) == 5:
        print("Intention changed")
        self.intention = self.desires['path1'][1]

      return None

    #Estoy en pos C4, hay alerta, no estoy en la posición de la cámara que mandó la alerta, no veo nada con visión computacional, cámara está arriba mío o cámara es C2-> dejar en path 1, ir a C3
    def rule_14(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False, False, False]

      # Proposición 1: Si estoy en C4
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path1'][4]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      # Proposición 4: Cámara está arriba
      if self.beliefs['cameras']['camera2'].has_alert == True or self.beliefs['cameras']['camera3'].has_alert == True:
        validator[3] = True

      # Proposición 5: No estoy en la posición de la cámara que envió la alerta
      if self.beliefs['own_position'].has_place.has_position != str(self.beliefs['camera_alert']):
        validator[4] = True

      if sum(validator) == 5:
        print("Intention changed")
        self.intention = self.desires['path1'][3]

      return None

    #Estoy en pos C2, hay alerta, no estoy en la posición de la cámara que mandó la alerta, no veo nada con visión computacional, cámara está a la derecha mía -> dejar en path 1, ir a C3
    def rule_15(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False, False, False]

      # Proposición 1: Si estoy en C2
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path1'][2]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      # Proposición 4: Cámara está a la derecha
      if self.beliefs['cameras']['camera3'].has_alert == True:
        validator[3] = True

      # Proposición 5: No estoy en la posición de la cámara que envió la alerta
      if self.beliefs['own_position'].has_place.has_position != str(self.beliefs['camera_alert']):
        validator[4] = True

      if sum(validator) == 5:
        print("Intention changed")
        self.intention = self.desires['path1'][3]

      return None

    #Estoy en pos C2, hay alerta, no estoy en la posición de la cámara que mandó la alerta, no veo nada con visión computacional, cámara está abajo mío o cámara es C4 -> dejar en path 1, ir a C1
    def rule_16(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False, False, False]

      # Proposición 1: Si estoy en C2
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path1'][2]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      # Proposición 4: Cámara está a abajo
      if self.beliefs['cameras']['camera1'].has_alert == True or self.beliefs['cameras']['camera4'].has_alert == True:
        validator[3] = True

      # Proposición 5: No estoy en la posición de la cámara que envió la alerta
      if self.beliefs['own_position'].has_place.has_position != str(self.beliefs['camera_alert']):
        validator[4] = True

      if sum(validator) == 5:
        print("Intention changed")
        self.intention = self.desires['path1'][1]

      return None

    #Estoy en pos C3, hay alerta, no estoy en la posición de la cámara que mandó la alerta, no veo nada con visión computacional, cámara está a la izquierda mía -> dejar en path 1, ir a C2
    def rule_17(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False, False, False]

      # Proposición 1: Si estoy en C3
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path1'][3]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      # Proposición 4: Cámara está a la izquierda
      if self.beliefs['cameras']['camera2'].has_alert == True:
        validator[3] = True

      # Proposición 5: No estoy en la posición de la cámara que envió la alerta
      if self.beliefs['own_position'].has_place.has_position != str(self.beliefs['camera_alert']):
        validator[4] = True

      if sum(validator) == 5:
        print("Intention changed")
        self.intention = self.desires['path1'][2]

      return None

    #Estoy en pos C3, hay alerta, no estoy en la posición de la cámara que mandó la alerta, no veo nada con visión computacional, cámara está abajo mío o cámara C1-> dejar en path 1, ir a C4
    def rule_18(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False, False, False, False, False]

      # Proposición 1: Si estoy en C3
      if self.beliefs['own_position'].has_place.has_position == str(self.desires['path1'][3]):
          validator[0] = True

      # Proposición 2: Hay alerta
      validator[1] = False
      for name, camera in self.beliefs['cameras'].items():
            if camera.has_alert == True:
              validator[1] = True

      # Proposición 3: No veo nada con visión computacional
      if not self.beliefs['seeing_prisioner'].has_existence:
        validator[2] = True

      # Proposición 4: Cámara está abajo
      if self.beliefs['cameras']['camera4'].has_alert == True or self.beliefs['cameras']['camera1'].has_alert == True:
        validator[3] = True

      # Proposición 5: No estoy en la posición de la cámara que envió la alerta
      if self.beliefs['own_position'].has_place.has_position != str(self.beliefs['camera_alert']):
        validator[4] = True

      if sum(validator) == 5:
        print("Intention changed")
        self.intention = self.desires['path1'][4]

      return None

    #Estoy en posición de la cámara que mandó la alerta y no veo nada con visión computacional -> Girar 360°
    def rule_19(self):
      """
      Regla deductiva para ir a la cámara
      """
      #Validador de regla
      validator = [False]

      # Proposición 1: Si estoy en la posición de la cámara que envió la alerta
      if self.beliefs['own_position'].has_place.has_position == str(self.beliefs['camera_alert']):
        validator[0] = True

      if sum(validator) == 1:
        self.turn_around

      return None

    #Giré 360° y no veo nada -> Seguir a la siguiente posición en el path actual
    #Estoy en posición de la cámara que mandó la alerta y veo algo con visión computacional: detenerme y avisar al policia / Iniciar comunicación


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
        print("NEXT-Position")
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

    def turn_around(self):
      pass
      
    def alert(self):
      self.plan = None
      self.intention = None
      self.idle()
      print("Communication with security agent")
      self.beliefs['seeing_prisioner'] = Prisioner(has_existence = False)
      
    def choose_camera(self):
      camera_names = ['camera1', 'camera2', 'camera3', 'camera4']
      cameras_with_alerts = []

      #Guardar todas las cámaras que tengan una alerta
      for camera in camera_names:
          if self.beliefs['cameras'][camera].has_alert:
              cameras_with_alerts.append(camera)

      #Si no hay cámaras con alertas regresa None
      if not cameras_with_alerts:
        return None

      #En caso de que haya sólo un elemento se regresa ese valor
      chosen_camera = eval(self.beliefs['cameras'][cameras_with_alerts[0]].has_place.has_position)

      #En caso de que haya más de una cámara que detectó movimiento, elegir la más cercana a mi posición
      shortest_distance = float('inf')


      if len(cameras_with_alerts) > 1:
        for i in cameras_with_alerts:

          #Restar tupla con mi posición y sumar valor absoluto
          distance = sum(abs(x) for x in tuple(a - b for a, b in zip(eval(self.beliefs['cameras'][i].has_place.has_position), self.model.grid.positions[self])))

          #Comparar con distancia anterior y reemplazar si es necesario
          if distance < shortest_distance:
            shortest_distance = distance
            chosen_camera = self.beliefs['cameras'][i].has_place.has_position

      return chosen_camera

    def move(self):
        if self.directionTag == 'N':
            self.model.grid.move_by(self, (0, 1))
        if self.directionTag == 'S':
            self.model.grid.move_by(self, (0, -1))
        if self.directionTag == 'E':
            self.model.grid.move_by(self, (1, 0))
        if self.directionTag == 'W':
            self.model.grid.move_by(self, (-1, 0))
        print(f"Moved to new position: {self.model.grid.positions[self]}")
        pass

    def turn(self, axis, distance):
        if axis == 'y' and distance < 0:
            return 'self.turnS()'
        elif axis == 'y' and distance > 0:
            return 'self.turnN()'
        elif axis == 'x' and distance < 0:
            return 'self.turnW()'
        elif axis == 'x' and distance > 0:
            return 'self.turnE()'
        else:
            return 'self.idle()'

    def turnN(self):
        self.direction = (0,-1) #Hacia Norte
        self.directionTag = "N"
        pass

    def turnS(self):
        self.direction = (0,1)  #Hacia Sur
        self.directionTag = "S"
        pass

    def turnE(self):
        self.direction = (-1,0) #Hacia Este
        self.directionTag = "E"
        pass

    def turnW(self):
        self.direction = (1,0) #Hacia Oeste
        self.directionTag = "W"
        pass

    def idle(self):
        pass


""" CamaraAgent """
## Camera Agent Logic
class CameraAgent(ap.Agent):
    def see(self, e):
        self.per = e
        return self.per

    def next(self, per):
        for rule in self.rules:
            act = rule(per)
            if act is not None:
                return act
        return None

    def action(self, act):
        if act:
            act()
        return None

    # Rule 1: if I identify a prisoner, send alert to dron
    def rule_1(self, per):
        validator = False

        if per == "Prisioner":
            validator = True

        if validator == True:
            return self.send_message
        return None

    def send_message(self):
        msg = Message("alert", "Prisioner detected.", "camera " + str(self.id), "Drone")
        self.model.broadcast.append(msg)
        #print_message(msg)
        pass

    def setup(self):
        self.agentType = 1
        self.rules = {
            self.rule_1
        }

    def step(self):
        env = ["Prisioner"]
        self.e = random.choice(env)
        self.per = self.see(self.e)
        self.act = self.next(self.per)
        if self.act is not None:
            self.action(self.act)
        return None


""" Dron """
## Drone Agent Logic (communication protocol)
class DronAgent(ap.Agent):
    def see(self, e):
        self.per = e
        return self.per

    def next(self, per):
        for rule in self.rules:
            act = rule(per)
            if act is not None:
                return act
        return None

    def action(self, act):
        if act:
            act()
        return None

    # Rule 1: if I have autonomy and I identify a prisoner and I don't have a plan, send alert to Security Guard
    def rule_1(self, per):
        validator = [False, False, False]

        if per == "Prisioner":
            validator[0] = True
        if self.executing_plan == False:
            validator[1] = True
        if self.autonomy == True:
            validator[2] = True

        if sum(validator) == 3:
            return self.send_message("alert")
        return None

    # Rule 2: if I have autonomy and a plan and I don't identify a prisioner, I return to my path
    def rule_2(self, per):
        validator = [False, False, False]

        if per != "Prisioner":
            validator[0] = True
        if self.executing_plan == True:
            validator[1] = True
        if self.autonomy == True:
            validator[1] = True

        if sum(validator) == 3:
            return self.returnToPath
        return None

    # Rule 3: if I have a plan and I identify a prisioner, I alert the guard
    def rule_3(self, per):
        validator = [False, False]

        if per == "Prisioner":
            validator[0] = True
        if self.executing_plan == True:
            validator[1] = True

        print(validator)
        if sum(validator) == 2:
            return self.send_message(self.performative, self.cam)
        return None

    # Rule 4: if I have autonomy and I don't identify a prisioner and get a message and it is from a camera, I go to the camera's location
    def rule_4(self, per):
        validator = [False, False, False]

        if per != "Prisioner":
            validator[0] = True
        if self.performative == "alert":
            validator[1] = True
        if self.autonomy == True:
            validator[2] = True

        if sum(validator) == 3:
            return self.plan_1(self.cam)
        return None

    # Rule 5: if I the guard asks for taking control, I allow it
    def rule_5(self, per):
        validator = False
        if self.performative == "take-control":
            validator = True

        if validator:
            return self.send_message("reply")
        return None

    # Rule 6: if I the guard asks for moving downwards, I allow it
    def rule_6(self, per):
        validator = [False]

        if self.performative == "move-down":
            validator[0] = True

        if sum(validator) == 1:
            return self.send_message("reply")
        return None

    # Rule 7: if I the guard asks for moving forward, I allow it
    def rule_7(self, per):
        validator = [False]

        if self.performative == "move-forward":
            validator[0] = True

        if sum(validator) == 1:
            return self.send_message("reply")
        return None

    # Rule 8: if I the guard asks for capturing, I allow it
    def rule_8(self, per):
        validator = [False]

        if self.performative == "capture":
            validator[0] = True

        if sum(validator) == 1:
            return self.send_message("capture")
        return None

    #Practicality
    def plan_1(self, camera): #if I get an alert from a camera I'm going to follow it and check again
        print("Executing plan 1")
        self.executing_plan = True
        self.followTarget(camera)
        print(camera)
        self.per = "Prisioner" ##Recibe de dron
        self.act = self.rule_3(self.per)
        self.action(self.act)
        #self.step()

    def receive(self, msg):
        self.inbox.append(msg)
        #print(f"Drone received message: {msg.performative} from {msg.sender}")
        pass

    def process_messages(self):
        #print(f"Processing messages. Inbox size: {len(self.inbox)}")
        if self.inbox:
            msg = self.inbox.popleft()
            self.performative = msg.performative
            print("performative: ", self.performative)
            self.cam = msg.sender
            print("sender: ", self.cam)
            if msg.performative == "take-control":
                self.autonomy = False
                self.send_message("reply", "take-control")
                print("Guard has taken control of the drone.")
                return
            elif msg.performative in ["move-down", "move-forward", "capture"]:
                self.send_message("reply", msg.performative)

    def send_message(self, performative, sender=None):
          content = self.get_content(performative, sender)
          if content is None:
              print(f"Invalid performative: {performative}")
              return

          msg = Message(performative, content, "Drone", "Security Guard")
          self.model.broadcast.append(msg)
          #print_message(msg)

    def get_content(self, performative, sender):
        if performative == "reply" and self.performative == "take-control":
            self.autonomy = False
            return "Guard has taken control of the drone."
        if performative == "alert":
            if sender is not None:
                return f"Prisoner detected at camera {sender}"
            else:
                return "Prisoner detected."
        elif performative == "take-control":
            self.autonomy = False
            return "Guard has taken control of the drone."
        elif performative == "reply":
            if self.moves == 0:
                self.moves = 1
                return "Drone has moved downwards."
            elif self.moves == 1:
                self.moves = 2
                return "Drone has moved forward."
        elif performative == "capture":
            return "Drone has captured the target successfully."
        return None


    def setup(self):
        self.position = 0
        self.autonomy = True
        self.moves = 0
        self.executing_plan = False
        self.inbox = deque()
        self.agentType = 0
        self.performative = ""
        self.cam = None
        self.rules = [
            self.rule_5,
            self.rule_1,
            self.rule_2,
            self.rule_3,
            self.rule_4,
            self.rule_6,
            self.rule_7,
            self.rule_8
        ]

    def step(self):
        env = ["Nothing"]
        self.e = random.choice(env)
        self.process_messages()
        if not self.autonomy:
            print("Drone is under guard control")
            return
        self.per = self.see(self.e)
        self.act = self.next(self.per)
        if self.act is not None:
            self.action(self.act)


    ## ACCIONES (para rellenar y/o cambiar)

    #esto es para ir a donde va la cámara
    def followTarget(self, camera):
        #self.position = self.model.cameras.position
        return True


    def returnToPath(self):
        self.executing_plan = False
        self.position = 0


""" SeguridadAgent """
## Security Personal Agent Logic
class SegurityAgent(ap.Agent):
    def see(self, e):
        self.per = e
        print(self.per)
        return self.per

    def next(self, per):
        if per == False:
            pass
        for rule in self.rules:
            act = rule(per)
            if act is not None:
                return act
        return None

    def action(self, act):
        if act:
            act()
        return None

    # Rule 1: if I receive an alert, I take control of the drone
    def rule_1(self, per):
        validator = False

        if self.performative == "take-control":
            validator = True

        self.control = True

        if validator == True:
            return self.take_control
        return None

    # Rule 2: if I receive an reply, I move the drone
    def rule_2(self, per):
        validator = False

        if self.performative != "alert" and self.performative != "take-control":
            validator = True

        if validator == True:
            return self.send_message(self.performative)
        return None

    def receive(self, msg):
        self.inbox.append(msg)
        print("Guard received message")
        pass

    def process_messages(self):
        if self.inbox:
            msg = self.inbox.popleft()
            if msg.performative == "alert":
                return "take-control"
            elif msg.performative == "reply" and self.moves == 0:
                self.moves = 1
                return "move-down"
            elif msg.performative == "reply" and self.moves == 1:
                self.moves = 2
                return "move-forward"
            elif msg.performative == "reply" and self.moves == 2:
                return "capture"
        return ""

    def send_message(self, performative):
        content = self.get_content(performative)
        if content is None:
            print(f"Invalid performative: {performative}")
            return

        msg = Message(performative, content, "Security Guard", "Drone")
        self.model.broadcast.append(msg)
        #print_message(msg)

    def get_content(self, performative):
        content_map = {
            "take-control": "Request for taking control of the drone.",
            "move-forward": "Move 1 meter towards the target",
            "move-down": "Move 1 meter downwards.",
            "capture": "Capture the target."
        }
        return content_map.get(performative)

    def setup(self):
        self.inbox = deque()
        self.moves = 0
        self.control = False
        self.agentType = 2
        self.performative = ""
        self.rules = {
            self.rule_1,
            self.rule_2
        }

    def step(self):
        if self.inbox:
            self.e = True
            self.performative = self.process_messages()
            self.per = self.see(self.e)
            self.act = self.next(self.per)
            if self.act is not None:
                self.action(self.act)
        else:
            self.e = False

        return None

    # ACCIONES
    def take_control(self):
        self.send_message("take-control")
        pass


class PrisonModel(ap.Model):
    def setup(self):
        self.drones = ap.AgentList(self, self.p.drones, DroneAgent)
        self.grid = ap.Grid(self, (self.p.M, self.p.N), track_empty=True)
        self.grid.add_agents(self.drones, positions=(self.p.dpos), random=False, empty=True)
        
        #Interactions
        self.cameras = ap.AgentList(self, self.p.cameras, CameraAgent)
        for camera, position in zip(self.cameras, self.p.positions):
            camera.position = position
        self.guard = ap.AgentList(self, self.p.guard, SegurityAgent)
        self.dron = ap.AgentList(self, self.p.dron, DronAgent)
        self.broadcast = deque()

    def step(self):
        self.drones.step(self.grid)
        self.cameras.step()
        self.process_messages("Drone")
        self.dron.step()
        self.process_messages("Security Guard")
        self.guard.step()
        
    def process_messages(self, receiver):
        messages = [msg for msg in self.broadcast if msg.receiver == receiver]
        for msg in messages:
            self.broadcast.remove(msg)
            if receiver == "Drone":
                self.dron.receive(msg)
                #print_message(msg)
            elif receiver == "Security Guard":
                self.guard.receive(msg)
                #print_message(msg)
    
    def update(self):
        pass

    def end(self):
        pass


# Global dictionary to store the model and index for each client
client_states = {}

def clean(string):
    cleaned_string = string.replace("self.", "").replace("()", "")
    return cleaned_string

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    if client_id in client_states:
        del client_states[client_id]
    print('Client disconnected')

@socketio.on('drone_handler')
def handle_drone(message):
    try:
        data = json.loads(message)
        client_id = request.sid
        if client_id not in client_states:
            parameters = {
                'drones': 1,
                'cameras': 1,
                'guard': 1,
                'steps': 2000,
                'M': 200,
                'N': 200,
                'positions': [(0, 119), (122, 119), (122, 0), (0, 0)],
                'dpos': [(50, 0)]
            }
            
            model = PrisonModel(parameters)
            result = model.setup()
            
            client_states[client_id] = {
                'model': model,
                'step_count': 0
            }
        
        client_state = client_states[client_id]
        model = client_state['model']
        step_count = client_state['step_count']
        
        if step_count < model.p.steps:
            model.step()
            client_state['step_count'] += 1
        
        if model.drones[0].actionU:
            print(f"ACTUIONU")    
            action = model.drones[0].actionU
        else:
            action = "idle"
        
        print(f"Command: {action}")
        
        clean_action = clean(action)    
        emit('drone_response', {'command': clean_action})
        

    except json.JSONDecodeError:
        print('Received invalid JSON:', message)
    except Exception as e:
        print(f"Error processing drone data: {str(e)}")


if __name__ == '__main__':
    print("Starting WebSocket server...")
    socketio.run(app, debug=True, port=5000)