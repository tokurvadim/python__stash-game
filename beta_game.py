import re

FIELD = [
    ['', '', '', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
    ['', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['', '3', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['', '4', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['', '5', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['', '6', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['', '7', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['', '8', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['', '9', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
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



def game():
    for line in FIELD:
        print(' '.join(line))
    try:
        cords = input('Welcome to game. Please, enter coordinate of your stash: ')
        #if len(re.search(r'[A-Ja-j]{1}\d{1}', cords)[0]) == len(cords) and len(cords) == 2:
        if re.search(r'[A-Ja-j]{1}\d{1}', cords)[0] == cords:
            FIELD[int(cords[1])][FIELD_INDEXES.get(cords[0].upper())] = 'X'
        else:
            raise IOError
    except Exception as error:
        print('input error')
        return game()

    else:
        print('pass')
        for line in FIELD:
            print(' '.join(line))


def create_connection(sock: socket):
    connection, host_client = sock.accept()
    with connection:
        username = ''
        print(f'Get request to connect from: {host_client}...')
        repr(connection.recv(1024))
        connection.sendto(b'Connection success.', host_client)
        while not username:
            connection.sendto(b'Please, enter your username:', host_client)
            username = connection.recv(1024)
        USERS[username.decode()] = host_client
        print(f'Successfully set user {username.decode()}.')
        connection.sendto('Welcome, {user}.Youve been successfully registered.'.format(user=username).encode(), host_client)
        while len(USERS) != 2:
            connection.sendto(b'Waiting for second player...', host_client)
            sleep(10)
        print('Both players has connected. The game is start.')
        connection.sendto(b'Second player has connected.', host_client)
        connection.sendall(b'The game is start.')
        return True


def game():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(HOST)
    sock.listen()
    while True:
        connection, host_client = sock.accept()
        with connection:
            username = ''
            print(f'Get request to connect from: {host_client}...')
            repr(connection.recv(1024))
            connection.sendto(b'Connection success.', host_client)
            while not username:
                connection.sendto(b'Please, enter your username:', host_client)
                username = connection.recv(1024)
            new_user = User(*host_client)
            USERS[username.decode()] = new_user
            print(USERS)
            print(f'Successfully register user {username.decode()}.')
            connection.sendto('Welcome, {user}. Youve been successfully registered.'.format(user=username.decode()).encode(),
                              host_client)
            connection.sendto(b'Waiting for second player...', host_client)
            if len(USERS) == 2:
                print('Both players has connected. The game is start.')
                connection.sendall(b'The game is start.')
            connection.sendall(b'Welcome to game!\n'
                               b'Your field')


game()
