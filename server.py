import socket
import re
import threading
import time

from exceptions import InputCordsError, InputUsernameError, WrongMoveError
from utils import FIELD_INDEXES, BARRIER, EVENT
from settings import USERS_COUNT, HOST


class Player:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.username = name
        self.field_moves = [
            ['', '', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
            ['1', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?'],
            ['2', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?'],
            ['3', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?'],
            ['4', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?'],
            ['5', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?'],
            ['6', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?'],
            ['7', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?'],
            ['8', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?'],
            ['9', '?', '?', '?', '?', '?', '?', '?', '?', '?', '?'],
        ]
        self.current_move = None
        self.stash_enemy = None

    @property
    def get_ip(self):
        return self.ip

    @property
    def get_port(self):
        return self.port


class Server:
    def __init__(self, host):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.HOST = host
        self.players_list = []

    def send_field(self, conn, client_socket, player):
        field_lines = []
        for line in player.field_moves:
            field_lines.append(' '.join(line) + '\n')
        field_to_bytes = 'Your field:\n' + ''.join(field_lines)
        conn.sendto(field_to_bytes.encode(), client_socket)

    def register_player(self, conn, client_socket):
        conn.sendto(b'Please, enter your username:', client_socket)
        try:
            print('flag first')
            username = conn.recv(1024).decode()
            print('flag sec')
            empty_username_flag = True
            for player in self.players_list:
                if username == player.username:
                    empty_username_flag = False
            if empty_username_flag:
                print(f'Successfully register player {username} with address: {client_socket}.')
                conn.sendto(
                    f'Welcome, {username}. Youve been successfully registered.'.encode(),
                    client_socket)
                new_player = Player(*client_socket, username)
                self.players_list.append(new_player)
                BARRIER.wait()
                BARRIER.reset()
                conn.sendto(b'Preparing for game.', client_socket)
                print('Both players has connected. Prepare for game...')
                return new_player
            else:
                raise InputUsernameError
        except InputUsernameError as error:
            conn.sendto(b'Error: This username is already taken. Try again.', client_socket)
            print(error)
            return self.register_player(conn, client_socket)

    def set_stash(self, conn, client_socket, username):
        conn.sendto(b'Enter coordinate of your stash: ', client_socket)
        try:
            cords = conn.recv(1024).decode().upper()
            match = re.findall(r'[A-J]\d', cords)
            if len(match) == 1 and match[0] == cords:
                for player in self.players_list:
                    if not client_socket == (player.get_ip, player.get_port):
                        player.stash_enemy = [int(cords[1]), FIELD_INDEXES.get(cords[0])]
                conn.sendto(b'Successfully set stash!', client_socket)
                print(f'Successfully set stash to player {username}.')
                BARRIER.wait()
                BARRIER.reset()
                conn.sendto(b'Get ready to start!', client_socket)
                time.sleep(1)
                for i in range(3, -1, -1):
                    conn.sendto(f'Game start in {i}...'.encode(), client_socket)
                    time.sleep(1)
            else:
                raise InputCordsError
        except InputCordsError as error:
            print(error)
            conn.sendto(b'Error: Invalid coordinate. Try again.', client_socket)
            return self.set_stash(conn, client_socket, username)

    def make_move_first(self, conn, client_socket, player):
        conn.sendto(b'Enter coordinate of your move: ', client_socket)
        try:
            cords = conn.recv(1024).decode().upper()
            match = re.findall(r'[A-J]\d', cords)
            if EVENT.is_set():
                conn.sendto(b'You lose! Another player found your stash!', client_socket)
                return True
            if len(match) == 1 and match[0] == cords:
                cords = [int(cords[1]), FIELD_INDEXES.get(cords[0])]
                player.current_move = cords
                if cords == player.stash_enemy:
                    player.field_moves[cords[0]][cords[1]] = 'X'
                    print(f'***Game end! Player {player.username} win!***')
                    conn.sendto(b'You find a stash! Congrats!', client_socket)
                    self.send_field(conn, client_socket, player)
                    return True
                else:
                    player.field_moves[cords[0]][cords[1]] = '+'
                    print(f'Player {player.username} make a move.')
                    conn.sendto(b'You make a move.', client_socket)
                    self.send_field(conn, client_socket, player)
                    return False
            else:
                raise WrongMoveError
        except WrongMoveError as error:
            print(error)
            conn.sendto(b'Error: Invalid move. Try again.', client_socket)
            return self.make_move_first(conn, client_socket, player)

    def make_move(self, conn, client_socket, player):
        conn.sendto(b'Enter direction of your move(u/r/d/l): ', client_socket)
        try:
            move = conn.recv(1024).decode().lower()
            match = re.findall(r'[urdl]', move)
            if EVENT.is_set():
                conn.sendto(b'You lose! Another player found your stash!', client_socket)
                return True
            if len(match) == 1 and match[0] == move:
                if move == 'u':
                    move = [player.current_move[0] - 1, player.current_move[1]]
                elif move == 'r':
                    move = [player.current_move[0], player.current_move[1] + 1]
                elif move == 'd':
                    move = [player.current_move[0] + 1, player.current_move[1]]
                elif move == 'l':
                    move = [player.current_move[0], player.current_move[1] - 1]

                if 1 <= move[0] <= 9 and 1 <= move[1] <= 10:
                    print(f'Get move from {player.username}.')
                    player.field_moves[player.current_move[0]][player.current_move[1]] = '.'
                    player.current_move = move
                    if move == player.stash_enemy:
                        player.field_moves[move[0]][move[1]] = 'X'
                        print(f'***Game end! Player {player.username} win!***')
                        conn.sendto(b'You find a stash! Congrats!', client_socket)
                        self.send_field(conn, client_socket, player)
                        return True
                    else:
                        player.field_moves[move[0]][move[1]] = '+'
                        print(f'Player {player.username} make a move.')
                        conn.sendto(b'You make a move.', client_socket)
                        self.send_field(conn, client_socket, player)
                        return False
                else:
                    raise WrongMoveError
            else:
                raise WrongMoveError
        except WrongMoveError as error:
            print(error)
            conn.sendto(b'Error: Invalid move. Try again.', client_socket)
            return self.make_move(conn, client_socket, player)

    def game_thread(self):
        while True:
            conn, client_socket = self.sock.accept()
            with conn:
                print(f'Set connect with client: {client_socket}. Waiting for register...')
                conn.sendto(b'Connection success.', client_socket)
                player = self.register_player(conn, client_socket)
                print(f'Send request to set stash to player: {player.username}...')
                self.set_stash(conn, client_socket, player.username)
                print('The game is start.')
                first_move = self.make_move_first(conn, client_socket, player)
                if first_move:
                    EVENT.set()
                    return True
                while True:
                    move = self.make_move(conn, client_socket, player)
                    if move:
                        EVENT.set()
                        return True

    def start(self):
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
    server = Server(HOST)
    server.start()
