from .base import BaseEntity

class Tenant(BaseEntity):
    def __init__(self, id, **kwargs):
        self.accountSid = ""
        self.authToken = ""
        self.domain = ""

        self.set_params(kwargs)
        BaseEntity.__init__(self, id)
