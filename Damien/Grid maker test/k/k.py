import turtle

class engineBattleShip:

    def __init__(self,sizeWidth,sizeHeight):
        self.display = turtle.Screen()
        self.clicTurtle = turtle.Turtle()
        self.clicTurtle._tracer(10,1000)
        self.display.setup(sizeWidth,sizeHeight)
        self.itemDictionary = {}
        self.turtleKiller = []
        self.x = 0
        self.y = 0
        

    '''
    Grid making function
    '''
    def drawGrid(self,itemName,nbHeight,margin,windowWidth,posX,posY,gridR,gridG,gridB):
        #Initiation of turtle
        pixelPerSquare = (windowWidth - 2*margin)/nbHeight
        compensation = windowWidth/2
        basicTurtle = turtle.Turtle()
        basicTurtle.hideturtle()
        basicTurtle.color(gridR,gridG,gridB)
        basicTurtle._tracer(10,1000)
        basicTurtle.penup()
        basicTurtle.setposition(-self.display._window_size()[0]/2 + posX + margin,self.display._window_size()[0]/2 - posY - margin)
        basicTurtle.pendown()
    
        #Adding items to itemDictionary
        self.itemDictionary[itemName] = [(windowWidth - 2*margin,windowWidth - 2*margin),(nbHeight,nbHeight)]
    
    
        #Drawing
        for x in range (4):
            basicTurtle.forward(windowWidth - 2*margin)
            basicTurtle.right(90)
    
        resetX = basicTurtle.pos()[0]
        resetY = basicTurtle.pos()[1]

        basicTurtle.right(90)
        for x in range (0,nbHeight):
           basicTurtle.penup()
           basicTurtle.setposition(basicTurtle.pos()[0] + pixelPerSquare,resetY)     
           basicTurtle.pendown()
           basicTurtle.forward(windowWidth - 2*margin)
           basicTurtle.penup()

        basicTurtle.setposition(resetX,resetY)
        basicTurtle.right(90)
        for y in range (0,nbHeight):
            basicTurtle.penup()
            basicTurtle.setposition(resetX,basicTurtle.pos()[1] - pixelPerSquare)
            basicTurtle.pendown()
            basicTurtle.back(windowWidth - 2*margin)
            basicTurtle.penup()

    '''
    Click Detection
    '''

    def clicManager(self):
        self.turtleKiller.append(turtle.Turtle())
        victimTurtle = self.turtleKiller[0]
        victimTurtle._tracer(10,1000)
        victimTurtle.penup()
        #victimTurtle.hideturtle()
        self.display.onscreenclick(victimTurtle.goto)
        print(victimTurtle.position())
        self.turtleKiller.clear()
        #for key in itemDictionary:
            #itemDictionary.get(key)[]

#(self,itemName,nbHeight,margin,windowWidth,posX,posY,gridR,gridG,gridB):
game = engineBattleShip(800,800)
game.drawGrid("Attack Grid",10,10,400,200,350,0,0,0)
game.drawGrid("Shot Grid",10,10,250,275,75,0,0,0)
while True:
    game.clicManager()