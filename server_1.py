from server import Server
from settings import HOST

if __name__ == '__main__':
    server = Server(HOST)
    server.start()
