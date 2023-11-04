class InputUsernameError(Exception):
    def __init__(self, message="---invalid username--- Sending repeat request."):
        print(message)


class InputCordsError(Exception):
    def __init__(self, message="---invalid coordinate--- Sending repeat request."):
        print(message)


class WrongMoveError(Exception):
    def __init__(self, message="---invalid move--- Sending repeat request."):
        print(message)
