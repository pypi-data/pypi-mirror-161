from base import BaseEntity

class Queue(BaseEntity):
    def __init__(self, id):
        BaseEntity.__init__(self, id)
