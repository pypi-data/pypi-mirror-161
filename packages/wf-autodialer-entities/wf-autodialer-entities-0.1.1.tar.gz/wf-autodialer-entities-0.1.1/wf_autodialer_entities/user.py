class User:
    def __init__(self):
        self.email = ""
        self.first_name = ""
        self.last_name = ""

    @property
    def name(self):
        return F"{self.first_name} {self.last_name}"
