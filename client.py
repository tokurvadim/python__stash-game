from utils import ERROR_LIST, GAMEOVER_MSG_LIST


class Client:
    def __init__(self, socket, host):
        self.socket = socket
        self.host = host

    def input_valid(self):
        while True:
            data = input().encode()
            if data:
                return data
            else:
                print('Please, input something:')
                continue

    def valid_check(self):
        while True:
            print(self.socket.recv(1024).decode())
            data = self.input_valid()
            self.socket.sendto(data, self.host)
            response = self.socket.recv(1024).decode()
            print(response)
            if response in ERROR_LIST:
                continue
            else:
                return True

    def get_field(self):
        print(self.socket.recv(1024).decode())

    def make_move(self):
        while True:
            print(self.socket.recv(1024).decode())
            cords = self.input_valid()
            self.socket.sendto(cords, self.host)
            response = self.socket.recv(1024).decode()
            print(response)
            if response in ERROR_LIST:
                continue
            elif response in GAMEOVER_MSG_LIST:
                self.get_field()
                return True
            else:
                self.get_field()
                return False

    def countdown(self):
        for _ in range(4):
            print(self.socket.recv(1024).decode())

    def start(self):
        try:
            print(f'Send request to connect to host: {self.host}...')
            self.socket.connect(self.host)
            print(self.socket.recv(1024).decode())
            set_username = self.valid_check()
            print(self.socket.recv(1024).decode())
            set_cords_stash = self.valid_check()
            print(self.socket.recv(1024).decode())
            self.countdown()
            while True:
                move_result = self.make_move()
                if move_result:
                    return True
        except ConnectionRefusedError:
            print('Failed to connect.')
            return self.start()
