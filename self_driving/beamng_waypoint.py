import json
import uuid


class BeamNGWaypoint:
    def __init__(self, name, position, persistentId=None):
        print("BeamNGWaypoint....................................... inistial ...........................................")
        self.name = name
        self.position = position
        self.persistentId = persistentId if persistentId else str(uuid.uuid4())

    def to_json(self):
        print(
            "BeamNGWaypoint....................................... to_json ...........................................")
        obj = {}
        obj['name'] = self.name
        obj['class'] = 'BeamNGWaypoint'
        obj['persistentId'] = self.persistentId
        obj['__parent'] = 'generated'
        obj['position'] = self.position
        obj['scale'] = [4, 4, 4]
        return json.dumps(obj)
