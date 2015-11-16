import turtle
display = turtle.Screen()
display.setup(800,800)

def drawGrid(nbHeight,margin,windowWeight,posX,posY,gridR,gridG,gridB,screen):
    #Initiation of turtle
    pixelPerSquare = (windowWeight - 2*margin)/nbHeight
    compensation = windowWeight/2
    basicTurtle = turtle.Turtle()
    basicTurtle.color(gridR,gridG,gridB)
    basicTurtle._tracer(10,1000)
    basicTurtle.penup()
    basicTurtle.setposition(-screen._window_size()[0]/2 + posX + margin,screen._window_size()[0]/2 - posY - margin)
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


drawGrid(11,10,400,200,350,0,0,0,display)
drawGrid(11,10,250,275,75,0,0,0,display)