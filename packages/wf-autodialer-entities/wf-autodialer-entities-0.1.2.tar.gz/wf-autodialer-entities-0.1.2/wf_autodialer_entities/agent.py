from .base import BaseEntity
from .user import User

class Agent(BaseEntity, User):
    def __init__(self, id, **kwargs):
        self.conference = None
        self.is_busy = False
        self.queue_type = None
        self.tenant = None
        
        self.set_params(kwargs)
        BaseEntity.__init__(self, id)
