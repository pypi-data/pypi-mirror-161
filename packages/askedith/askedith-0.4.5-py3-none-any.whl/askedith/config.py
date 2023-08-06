class Config:
    def __init__(self) -> None:
        self.API_URL = "https://askedith-function-app.azurewebsites.net"


# Config is an object so that we can edit values during testing
config = Config()
