import agentpy as ap
import ast

## Camera Agent Logic
class CameraAgent(ap.Agent):
    def see(self, e):
        e = '[' + e + ']' # e is the environment 
        self.per = e
        self.per = list(ast.literal_eval(e)) # TODO: computer vision
        print(self.per)
        return self.per
    
    def next(self, per):
        for rule in self.rules:
            act = rule(per)
            if act is not None:
                return act
        return None
    
    # Rules
    # ...
    
    # Rule 1: if I identify a prisoner, send alert to dron
    def rule_1(self, per, receiver):
        validator = False
        for object in per:
            if object == receiver:
                validator = True
        
        if validator:
            return "alert"
        pass
    
    def setup(self):
        self.agentType = 1
        self.receiver = "prisoner"
        self.rules = (
            self.rule_1
        )
    
    def step(self, e):
        self.per = self.see(e)
        self.act = self.next(self.per)
        if self.act is not None:
            print(self.act)
            return self.act
        return None
    
    def alert(self):
        print("Alerting dron")
        pass


class WarehouseModel(ap.Model):
    def setup(self):
        self.camera = ap.AgentList(self, self.p.camera, CameraAgent)

    def step(self):
        for unit in self.camera:
            action = unit.step(self.p.environment)
            if action:
                getattr(unit, action)()  # Call the action method

    def update(self):
        pass

    def end(self):
        pass