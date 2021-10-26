import RPi.GPIO as gpio


g.setmode(g.BCM)

g.setup(2, g.OUT, initial= g.LOW)
g.setup(3, g.OUT, initial= g.LOW)
g.setup(4, g.OUT, initial= g.LOW)


def move(value):
    g.output(2, value)
    g.output(4,True)
    g.output(4,False)


def commit():
    g.output(3, True)
    g.output(3,False)

def update_state(position, value):
    high = position*2 + value
    for i in range(high-1):
        move(False)
    move(True)
    for i in range(32-high):
        move(False)
    commit()
    
    for i in range(32):
        move(False)
    commit()
        
    
