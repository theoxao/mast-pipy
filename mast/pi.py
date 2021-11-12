import RPi.GPIO as g
from time import sleep

g.setmode(g.BCM)

g.setup(2, g.OUT, initial= g.LOW)
g.setup(3, g.OUT, initial= g.LOW)
g.setup(4, g.OUT, initial= g.LOW)


def move(value):
    g.output(2, value)
    g.output(4,False)
    g.output(4,True)


def commit():
    g.output(3, True)
    g.output(3, False)


def update_state(position, value):
    high = position*2 + int(value)
    for i in range(high-1):
        move(False)
        sleep(0.05)
    move(True)
    for i in range(32-high):
        move(False)
        sleep(0.05)
    commit()
    for i in range(32):
        move(False)
        sleep(0.05)
    commit()
    sleep(0.1)
        
    
