class User:
    def __init__(self):
        self.email = ""
        self.first_name = ""
        self.last_name = ""

    @property
    def name(self):
        if hasattr(self, 'first_name') and hasattr(self, 'last_name'):
            return F"{self.first_name} {self.last_name}"
        return ''