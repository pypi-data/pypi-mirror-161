from .base import BaseEntity
from .user import User

class Opportunity(BaseEntity, User):
    def __init__(self, id, **kwargs):
        self.phone = ""
        self.country = ""
        self.state = ""

        self.set_params(kwargs)
        BaseEntity.__init__(self, id)
