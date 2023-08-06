from .base import BaseEntity

class Conference(BaseEntity):
    def __init__(self, id, **kwargs):
        self.caller = ""
        self.friendly_name = ""
        self.total_participants = 0
        
        self.set_params(kwargs)
        BaseEntity.__init__(id)
