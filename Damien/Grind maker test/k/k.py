import turtle
import random
import time
display = turtle.Screen()
display.setup(500,500)
backColor = 'White'
gridColor = 'Black'

def woah():
    screen.bgcolor(random.uniform(0,1),random.uniform(0,1),random.uniform(0,1))

def drawGrid(nbHeight,margin):
    #Initiation of turtle
    pixelPerSquare = int((display._window_size()[0] - 2*margin)/nbHeight)
    compensation = int(display._window_size()[0]/2)
    print(pixelPerSquare)
    basicTurtle = turtle.Turtle()
    basicTurtle._tracer(10,1000)
    basicTurtle.color(gridColor)
    basicTurtle.penup()
    basicTurtle.setposition(-compensation + margin,compensation - margin)
    basicTurtle.pendown()
    
    #Drawing
    for x in range (4):
        basicTurtle.forward(display._window_size()[0] - 2*margin)
        basicTurtle.right(90)

    for x in range (0,nbHeight):
        for y in range (0,nbHeight):
            for w in range (4):
                basicTurtle.forward(pixelPerSquare)
                basicTurtle.right(90)
            basicTurtle.forward(pixelPerSquare)
        basicTurtle.backward(display._window_size()[0] - 2*margin)
        basicTurtle.right(90)
        basicTurtle.forward(pixelPerSquare)
        basicTurtle.left(90)


drawGrid(10,10)
"""
while True:
    screen.title(start_time)


screen.onkey(woah,"w")
"""