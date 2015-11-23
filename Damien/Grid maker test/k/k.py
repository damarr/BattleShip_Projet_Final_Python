import turtle
import time
import os
import webbrowser

class engineBattleShip:
    def __init__(self,sizeWidth,sizeHeight):
        self.display = turtle.Screen()
        self.whileValue = True
        self.clicTurtle = turtle.Turtle()
        self.display.setup(sizeWidth,sizeHeight)
        self.itemDictionary = {}
        self.turtleKiller = []
        self.x = 0
        self.y = 0
        self.startTime = 0
        self.title = ''
        self.caseX = None
        self.caseY = None
        
    '''
    Efface tout dans la fenêtre
    '''

    def clear(self):
        self.display.clear()

    def getWhileValue(self):
        return self.whileValue

    '''
    Change le fond d'écran de la fenêtre
    '''

    def bgImage(self,path):
        self.display.bgpic(os.path.abspath(path))

    '''
    Crée des boutons qui prennent l'apparence d'images
    Besoin: Nom de l'objet, "path" de l'image, position en X et en Y, largeur et hauteur de l'image.
    '''

    def button(self,name,path,posX,posY,lenght,height): #not 100% good yet
        imageTurtle = turtle.Turtle()
        imageTurtle.penup()
        self.display.addshape(os.path.abspath(path))
        imageTurtle.shape(os.path.abspath(path))
        imageTurtle.goto(posX,posY)
        #[(windowWidth - 2*margin,windowWidth - 2*margin),(nbHeight,nbHeight),(posX,posY),(rawX,rawY)]
        self.itemDictionary[name] = [(lenght,height),(0,0),(0,0),(posX - (lenght/2),posY + (height/2))]

    '''
    Permet de changer de partie du programme
    '''

    def startButton(self):
        self.whileValue = False

    '''
    Quite le programme.
    '''

    def exitButton(self):
        self.display.bye()

    '''
    Ouvre une page internet.
    '''

    def infoButton(self):
        webbrowser.open("https://github.com/Damfurrywolf/BattleShip_Projet_Final_Python")

    '''
    Envoie une "notification à l'utilisateur en changeant le titre de la fenêtre"
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
    Fonction qui crée des grilles.
    Besoin: d'un nom pour la grille, le nombre de cases en largeur ou hauteur, l'espace désiré laissé sur les côtés,
    une position en X et en Y, une couleur en style RGB our la couleur de la grille et une couleur en type RGB pour le remplisage
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
    Retourne la position de l'item entré.
    '''

    def getRawItemPosition(self,name):
        return(self.itemDictionary.get(name)[3])

    '''
    Permet d'obtenir le nombre de cases en largeur et en hauteur d'une grille entrée (Une valeur car même nombre de cases dans les deux sens).
    '''

    def getGridSquareSize(self,name):
        stuff = self.itemDictionary.get(name)[1]
        return(stuff[0])
    
    '''
    Permet d'obtenir la largeur et la hauteur dans un tuple d'un objet entré.
    '''

    def getItemSize(self,name):
        return(self.itemDictionary.get(name)[0])

    '''
    Détecte les clics de l'utilisateur et retourne l'item cliqué ainsi que la position du clic.
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
                if (posX >= posXItem and posX <= posXItem + lenght) and (posYItem >= posY and posY >= posYItem - height):
                    self.clicTurtle.goto(0,0)
                    return((key,(posX,posY)))
        self.turtleKiller.clear()

    '''
    Retourne la position en X et en Y de la case cliquée par l'utilisateur
    '''

    def gridDecomposer(self,name,clicPosition):
        for key in self.itemDictionary:
            if key == name:
                temp = self.itemDictionary.get(key)[0]
                temp2 = self.itemDictionary.get(key)[1]
                tempPosition = self.itemDictionary.get(key)[3]
                pixelPerSquare = temp[0]/temp2[0]
                clicPosition2 = clicPosition[1]
                for x in range (temp2[0] + 1):
                    if clicPosition2[0] < ((x * pixelPerSquare) + tempPosition[0]):
                        self.caseX = x
                        break
                for y in range (temp2[1] + 1):
                    if (clicPosition2[1] > (tempPosition[1] - (y * pixelPerSquare))):
                        self.caseY = y
                        break
        positionX = ((x -1) * pixelPerSquare) + tempPosition[0]
        positionY = tempPosition[1] - ((y - 1) * pixelPerSquare)
        positionFinal = (positionX,positionY)
        return(positionFinal)

    '''
    Retourne la case cliquée en case et non en pixel
    '''

    def getClickedSquare(self):
        if self.caseX != None and self.caseY != None:
            transitionX = self.caseX
            transitionY = self.caseY
            self.caseX = None
            self.caseY = None
            return ((transitionX,transitionY))
    
    '''
    Pernet de gérer n'importe quel item ajouté dans le dictionaire d'items
    '''

    def itemDetector(self,clicPosition):
        if (clicPosition != None):
            for key in self.itemDictionary:
                if (key == clicPosition[0]):
                    shortcut = self.itemDictionary.get(key)
                    if (shortcut[1] != (0,0)):
                        self.gridDecomposer(key,clicPosition) # Si c'est une grid execute le programme qui renvoit la coordonée de la case
                    elif (shortcut[1] == (0,0)):
                        if key == "start":
                            self.startButton()
                        elif key == "exit":
                            self.exitButton()
                        elif key == "infos":
                            self.infoButton()


'''
Main pour tester les fonctionnalitées
'''
game = engineBattleShip(800,800)
game.bgImage("image\Background.gif")
game.drawGrid("Attack Grid",10,10,400,200,350,0,0,0,102,102,255)
game.drawGrid("Shot Grid",10,10,250,275,75,0,0,0,102,102,255)
game.button('start',"image\\gifButtons\\start.gif",-330,330,150,150)
game.button("infos","image\\gifButtons\\Credits.gif",-350,-340,80,80)
game.button("exit","image\\gifButtons\\exit.gif",330,340,100,100)
while game.getWhileValue():
    game.itemDetector(game.clicManager())
print("You have now started the game")
while True:
    game.windowTitleNotification("-_-It's your turn-_-","_-_IT'S YOUR TURN_-_",0.5)
    game.itemDetector(game.clicManager())