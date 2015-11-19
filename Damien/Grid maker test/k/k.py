import turtle
import time

class engineBattleShip:

    def __init__(self,sizeWidth,sizeHeight):
        self.display = turtle.Screen()
        self.clicTurtle = turtle.Turtle()
        self.display.setup(sizeWidth,sizeHeight)
        self.itemDictionary = {}
        self.turtleKiller = []
        self.x = 0
        self.y = 0
        self.startTime = 0
        self.title = ''
        
    '''
    Clears the window
    '''

    def clear(self):
        self.display.clear()

    '''
    Sets a background to the window
    '''

    def bgImage(self,path):
        self.display.bgpic(path)

    '''
    Send notifications as the title of the game window
    '''
    def windowTitleNotification(self,text1,text2,timeToElapse):
        timeNow = time.time()
        if (timeNow - self.startTime) >= timeToElapse:
            if self.title == text1:
                self.title = text2
                self.display.title(text2)
            elif self.title == text2:
                self.title = text1
                self.display.title(text1)
            else:
                self.title = text1
                self.display.title(text1)
            self.startTime = time.time()

    '''
    Grid making function
    '''

    def drawGrid(self,itemName,nbHeight,margin,windowWidth,posX,posY,PengridR,PengridG,PengridB,FillgridR,FillgridG,FillgridB):
        #Initiation of turtle
        pixelPerSquare = (windowWidth - 2*margin)/nbHeight
        compensation = windowWidth/2
        basicTurtle = turtle.Turtle()
        basicTurtle.hideturtle()
        basicTurtle.pencolor(PengridR/255,PengridG/255,PengridB/255)
        basicTurtle.fillcolor(FillgridR/255,FillgridG/255,FillgridB/255)
        basicTurtle._tracer(10,1000)
        basicTurtle.penup()
        basicTurtle.setposition(-self.display._window_size()[0]/2 + posX + margin,self.display._window_size()[0]/2 - posY - margin)
        rawX = basicTurtle.position()[0]
        rawY = basicTurtle.position()[1]
        basicTurtle.pendown()
    
        #Adding items to itemDictionary
        self.itemDictionary[itemName] = [(windowWidth - 2*margin,windowWidth - 2*margin),(nbHeight,nbHeight),(posX,posY),(rawX,rawY)]
    
    
        #Drawing
        basicTurtle.begin_fill()
        for x in range (4):
            basicTurtle.forward(windowWidth - 2*margin)
            basicTurtle.right(90)
        resetX = basicTurtle.pos()[0]
        resetY = basicTurtle.pos()[1]
        basicTurtle.end_fill()

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
        self.turtleKiller.append(self.clicTurtle)
        victimTurtle = self.turtleKiller[0]
        victimTurtle._tracer(10,1000)
        victimTurtle.penup()
        victimTurtle.hideturtle()
        self.display.onscreenclick(victimTurtle.goto)
        posX = victimTurtle.position()[0]
        posY = victimTurtle.position()[1]
        if posX != 0.00 and posY != 0.00:
            for key in self.itemDictionary:
                temp = self.itemDictionary.get(key)[0]
                lenght = temp[0]
                height = temp[1]
                temp = self.itemDictionary.get(key)[3]
                posXItem = temp[0]
                posYItem = temp[1]
                print(posX,posY)
                if (posX >= posXItem and posX <= posXItem + lenght) and (posYItem >= posY and posY >= posYItem - height):
                    return key
        self.turtleKiller.clear()


'''
Main
'''
game = engineBattleShip(800,800)
game.drawGrid("Attack Grid",10,10,400,200,350,0,0,0,102,102,255)
game.drawGrid("Shot Grid",10,10,250,275,75,0,0,0,102,102,255)


while True:
    game.windowTitleNotification("-_-It's your turn-_-","_-_IT'S YOUR TURN_-_",0.5)
    print(game.clicManager())
    