class Client:
    def __init__(self, Model) -> None:
        self.Model = Model
    def generate_response(self, user_message: str) -> str:
        return self.Model.generate_response(user_message)