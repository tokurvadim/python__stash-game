import socket
import re
import threading

users = {

}

USERS_COUNT = 2

HOST = ('127.0.0.1', 9999)

sem = threading.BoundedSemaphore(value=USERS_COUNT)


class User:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name
        self.field = FIELD

    @property
    def get_ip(self):
        return self.ip

    @property
    def get_port(self):
        return self.port

    @property
    def get_name(self):
        return self.name


FIELD = [
    ['', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
    ['1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['3', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['4', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['5', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['6', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['7', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['8', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['9', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['10', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
]

FIELD_INDEXES = {
    'A': 2,
    'B': 3,
    'C': 4,
    'D': 5,
    'E': 6,
    'F': 7,
    'G': 8,
    'H': 9,
    'I': 10,
    'J': 11,
}


class Game:
    def __init__(self, host):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = host
        self.player1 = None
        self.player2 = None
        self.players_list = []

    def register_player(self, conn, client_socket):
        conn.sendto(b'Please, enter your username:', client_socket)
        try:
            username = conn.recv(1024).decode()
            if username and username not in users.keys():
                print(f'Successfully register player {username} with address: {client_socket}.')
                conn.sendto(
                    f'Welcome, {username}. Youve been successfully registered.'.encode(),
                    client_socket)
                new_user = User(*client_socket, username)
                if users.keys():
                    self.player2 = new_user
                    self.players_list.append(self.player2)
                else:
                    self.player1 = new_user
                    self.players_list.append(self.player1)
                    conn.sendto(b'Waiting for second player...', client_socket)
                users[username] = client_socket
                return username
            else:
                raise IOError
        except IOError:
            conn.sendto(b'Error: Invalid username or this username is already taken. Try again.', client_socket)
            print('---invalid username--- Sending repeat request.')
            return self.register_player(conn, client_socket)

    def set_stash(self, conn, client_socket):
        conn.sendto(b'Please, enter coordinate of your stash: ', client_socket)
        try:
            cords = conn.recv(1024).decode()
            # if len(re.search(r'[A-Ja-j]{1}\d{1}', cords)[0]) == len(cords) and len(cords) == 2:
            if re.search(r'[A-Ja-j]{1}\d{1}', cords)[0] == cords:
                for player in self.players_list:
                    if client_socket == (player.get_ip, player.get_port):
                        player.field[int(cords[1])][FIELD_INDEXES.get(cords[0].upper())] = 'X'
                for line in FIELD:
                    conn.sendto(' '.join(line).encode(), client_socket)
            else:
                raise IOError
        except IOError:
            print('---invalid coordinate--- Sending repeat request.')
            conn.sendto(b'Error: Invalid coordinate. Try again.', client_socket)
            return self.set_stash(conn, client_socket)

    def game_thread(self):
        # self.sock.bind(HOST)
        # self.sock.listen()
        while True:
            conn, host_client = self.sock.accept()
            sem.acquire()
            with conn:
                print(f'Set connect with client: {host_client}. Waiting for register...')
                conn.sendto(b'Connection success.', host_client)
                username = self.register_player(conn, host_client)
                sem.release()
                while True:
                    if len(users) == USERS_COUNT:
                        conn.sendto(b'The game is start.', host_client)
                        break
                print('Both players has connected. The game is start.')
                print(f'Send request to set stash to player: {username}...')
                self.set_stash(conn, host_client)

    def start_game(self):
        self.sock.bind(HOST)
        self.sock.listen()
        print('Server is start and listen...')
        threads = []
        for _ in range(USERS_COUNT):
            t = threading.Thread(target=self.game_thread)
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()


if __name__ == '__main__':
    game = Game(HOST)
    game.start_game()
