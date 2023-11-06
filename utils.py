from threading import Barrier, Event

from settings import USERS_COUNT

ERROR_LIST = [
    'Error: This username is already taken. Try again.',
    'Error: Invalid coordinate. Try again.',
    'Error: Invalid move. Try again.',
]

GAMEOVER_MSG_LIST = [
    'You found a stash! Congrats!',
    'You lose! Another player found your stash!',
]

FIELD_INDEXES = {
    'A': 1,
    'B': 2,
    'C': 3,
    'D': 4,
    'E': 5,
    'F': 6,
    'G': 7,
    'H': 8,
    'I': 9,
    'J': 10,
}

THREAD_BARRIER = Barrier(USERS_COUNT)
THREAD_EVENT = Event()
