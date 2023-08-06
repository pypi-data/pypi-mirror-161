class Context:
    name: str
    host: str
    user: str
    password: str

    def __init__(self, name: str, host: str, user: str, password: str):
        self.name = name
        self.host = host
        self.user = user
        self.password = password

    def to_dict(self):
        return {
            "name": self.name,
            "host": self.host,
            "user": self.user,
            "password": self.password
        }
