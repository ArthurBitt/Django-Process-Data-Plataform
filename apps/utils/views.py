from config.settings import SLEEPING_PARAMS

from random import randint
from time import sleep

random_number = 0
def sleeping():
    global random_number

    param0 = int(SLEEPING_PARAMS[0])
    param1 = int(SLEEPING_PARAMS[1])
    param2 = int(SLEEPING_PARAMS[2])

    seconds = randint(param0, param1)
    if (seconds - random_number) > param2 or (
        random_number - seconds
    ) > param2:
        random_number = seconds
        sleep(seconds)
        return

    sleeping()
