import turtle
display = turtle.Screen()
display.setup(800,800)
itemDictionnary = {}

'''
Grid making function
'''

def drawGrid(itemName,itemDictionnary,nbHeight,margin,windowWeight,posX,posY,gridR,gridG,gridB,screen):
    #Initiation of turtle
    pixelPerSquare = (windowWeight - 2*margin)/nbHeight
    compensation = windowWeight/2
    basicTurtle = turtle.Turtle()
    basicTurtle.hideturtle()
    basicTurtle.color(gridR,gridG,gridB)
    basicTurtle._tracer(10,1000)
    basicTurtle.penup()
    basicTurtle.setposition(-screen._window_size()[0]/2 + posX + margin,screen._window_size()[0]/2 - posY - margin)
    basicTurtle.pendown()
    
    #Adding items to itemDictionnary
    itemDictionnary[itemName] = [(windowWeight - 2*margin,windowWeight - 2*margin),(nbHeight,nbHeight)]
    
    
    #Drawing
    for x in range (4):
        basicTurtle.forward(windowWeight - 2*margin)
        basicTurtle.right(90)
    
    resetX = basicTurtle.pos()[0]
    resetY = basicTurtle.pos()[1]

    basicTurtle.right(90)
    for x in range (0,nbHeight):
       basicTurtle.penup()
       basicTurtle.setposition(basicTurtle.pos()[0] + pixelPerSquare,resetY)     
       basicTurtle.pendown()
       basicTurtle.forward(windowWeight - 2*margin)
       basicTurtle.penup()

    basicTurtle.setposition(resetX,resetY)
    basicTurtle.right(90)
    for y in range (0,nbHeight):
        basicTurtle.penup()
        basicTurtle.setposition(resetX,basicTurtle.pos()[1] - pixelPerSquare)
        basicTurtle.pendown()
        basicTurtle.back(windowWeight - 2*margin)
        basicTurtle.penup()

'''
Click Detection
'''



drawGrid("Attack Grid",itemDictionnary,10,10,400,200,350,0,0,0,display)
drawGrid("Shot Grid",itemDictionnary,10,10,250,275,75,0,0,0,display)