import socket

from server import HOST
from client import Client

if __name__ == '__main__':
    client = Client(socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM), host=HOST)
    client.start()
