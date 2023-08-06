import json

class BaseEntity:
    def __init__(self, id):
        self.id = id

    def set_params(self, params):
        for key, value in params.items():
            try:
                setattr(self, key, value)
            except AttributeError as e:
                pass
    
    def to_dict(self):
        return self.__dict__
    
    def to_json(self):
        return json.dumps(self.to_dict())
