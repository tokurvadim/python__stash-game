import socket

from exceptions import ERROR_LIST
from server import FIELD, HOST


def print_field(sock):
    for _ in range(len(FIELD)):
        line = sock.recv(1024).decode()
        print(line)


def valid_check(host, sock):
    while True:
        print(sock.recv(1024).decode())
        name = input().encode()
        sock.sendto(name, host)
        while True:
            response = sock.recv(1024).decode()
            if response:
                print(response)
                break
        if response in ERROR_LIST:
            continue
        else:
            break
    return True


def make_connection(host, sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)):
    sock.connect(host)
    print(f'Send request to connect to host: {host}')
    print(sock.recv(1024).decode())
    set_username = valid_check(host, sock)
    print(sock.recv(1024).decode())
    print(sock.recv(1024).decode())
    print(sock.recv(1024).decode())
    while sock.recv(1024).decode() != 'The game is start.':
        pass
    print(sock.recv(1024).decode())
    set_cords_stash = valid_check(host, sock)
    print(set_cords_stash)
    return True


make_connection(HOST)
