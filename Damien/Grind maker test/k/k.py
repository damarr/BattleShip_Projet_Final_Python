import turtle
import random
import time
display = turtle.Screen()
display.setup(800,800)
backColor = 'White'
gridColor = 'Blue'

def woah():
    screen.bgcolor(random.uniform(0,1),random.uniform(0,1),random.uniform(0,1))

def drawGrid(nbHeight,margin,windowWeight,posX,posY,screen):
    #Initiation of turtle
    pixelPerSquare = (windowWeight - 2*margin)/nbHeight
    compensation = windowWeight/2
    print(pixelPerSquare)
    basicTurtle = turtle.Turtle()
    basicTurtle._tracer(10,1000)
    basicTurtle.color(gridColor)
    basicTurtle.penup()
    basicTurtle.setposition(-screen._window_size()[0]/2 + posX + margin,screen._window_size()[0]/2 - posY - margin)
    #basicTurtle.setposition(-compensation + margin,compensation - margin)
    basicTurtle.pendown()
    
    
    #Drawing
    for x in range (4):
        basicTurtle.forward(windowWeight - 2*margin)
        basicTurtle.right(90)

    for x in range (0,nbHeight):
        for y in range (0,nbHeight):
            for w in range (4):
                basicTurtle.forward(pixelPerSquare)
                basicTurtle.right(90)
            basicTurtle.forward(pixelPerSquare)
        basicTurtle.backward(windowWeight - 2*margin)
        basicTurtle.right(90)
        basicTurtle.forward(pixelPerSquare)
        basicTurtle.left(90)


drawGrid(11,10,400,200,350,display)
drawGrid(11,10,250,275,75,display)
#drawGrid(10,10,500/2,500,500)
"""
while True:
    screen.title(start_time)


screen.onkey(woah,"w")
"""