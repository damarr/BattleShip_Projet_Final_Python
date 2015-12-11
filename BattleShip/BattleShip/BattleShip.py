#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Description du module
"""
__auteur__ = "NACHI16"
__date__ = "2015-12-11"
__coequipiers__ = "IDUL", "IDUL"

#import standard modules
import json, socket, time, turtle, os, webbrowser, argparse, sys

class ClientReseau(object):
    """Client réseau pour jeu en-ligne.
    :param pseudo: votre pseudonyme.
    :param adversaire: le pseudonyme de l'adversaire que vous désirez affronter,
    None fera un pairage aléatoire.
    :param serveur: l'adresse ou le nom de l'hôte du serveur de jeu.
    :param port: le port du serveur de jeu."""

    def __init__(self, pseudo, adversaire, serveur='python.gel.ulaval.ca',
                port=31415):
        ''' Initialisation du jeu '''
        self.pseudo = pseudo
        self.adv = adversaire
        self.serveur = serveur
        self.port = port
        self.socket = socket.create_connection((self.serveur, self.port))
        self.tampon = ""
        partie = self.__connecter()
        self.attaque_envoyee = False
        self.rapport_envoyee = False
        if self.adv is None:
            if partie['hote'] != self.pseudo:
                self.adv = partie['adversaire']
            else:
                self.adv = partie['hote']

    def adversaire(self):
        """Retourne le pseudonyme de votre adversaire."""
        return self.adv

    def __connecter(self):
        """ Communique avec le serveur de jeu pour créer une partie.
        :returns: un dictionnaire contenant une clé 'joueurs' à laquelle
        est associée un tuple de pseudonymes de joueurs. """
        requete = {"requête": "créer", "pseudo": self.pseudo, "adversaire":
                   self.adv}
        self.__envoyer(requete)
        return self.__recevoir_sync()

    def __envoyer(self, requete):
        """Envoie une requête au serveur de jeu sous la forme d'une chaîne
        de caractères JSON.
        """
        self.socket.sendall(bytes("\x02" + json.dumps(requete) + "\x03",
                                 "utf-8"))

    def __recevoir(self):
        """Reçoit du serveur de jeu une chaîne de caractères et retourne
        un dictionnaire ou None si aucune réponse valide n'a été reçue.
        """
        self.tampon += str(self.socket.recv(4096), "utf-8")
        fin = self.tampon.rfind("\x03")
        debut = self.tampon[:fin].rfind("\x02")

        if debut < 0 or fin < 0:
            return None

        try:
            reponse = json.loads(self.tampon[debut + 1:fin])
        except ValueError:
            raise ValueError("Le serveur nous a répondu un message "
                             "incompréhensible: '{}'".format(self.tampon))
        else:
            self.tampon = self.tampon[fin + 1:]

        if "erreur" in reponse:
            raise Exception(reponse["erreur"])
        if reponse.get('requête') == 'protester':
            raise Protestation(reponse['message'])
        return reponse

    def attaquer(self, cellule=None):
        """Transmet au serveur la cellule de votre attaque. Cette cellule est 
        constituée d'un tuple de deux indices compris entre 0 et 9.
        
        :param cellule: La cellule à attaquer sous la forme d'un tuple de deux
        indices compris entre 0 et 9. Pour vérifier si la réponse de 
        l'adversaire est arrivée, il faut mettre l'argument à None.
        :return: La cellule attaquée par votre adversaire si celle-ci est
        disponible; None autrement.

        Cette fonction retourne None si aucune réponse de votre adversaire 
        n'a été obtenue à temps par le serveur de jeu. Dans ce cas, vous 
        devez rappeler la fonction sans argument jusqu'à ce vous obteniez une
        réponse (de préférence, introduire un délai entre les appels)."""
        assert cellule is None or self.attaque_envoyee == False, ("Vous devez" 
                    " attendre la réponse avant d'envoyer une nouvelle attaque")
        if cellule is not None:
            requete = {'requête': 'attaquer', 'cellule': cellule}
            self.__envoyer(requete)
            self.attaque_envoyee = True
        reponse = self.__recevoir_async()
        if reponse is not None:
            self.attaque_envoyee = False
            print(reponse)
            return reponse['cellule']
        else:
            return None

    def rapporter(self, message=None):
        """Rapporte au serveur le message du résultat de la dernière 
        attaque de votre adversaire.

        :param message: la chaîne de caractères de votre rapport.
        :returns: Le rapport de votre adversaire s'il est disponible; 
        None autrement.

        Cette fonction retourne None si aucune réponse de votre adversaire 
        n'a été obtenue à temps par le serveur de jeu. 
        Dans ce cas, vous devez rappeler la fonction sans argument jusqu'à 
        ce vous obteniez une réponse (de préférence, introduire un 
        délai entre les appels)."""

        assert message is None or not self.attaque_envoyee, ("Vous devez" 
                    " attendre la réponse avant d'envoyer un nouveau rapport")
        if message is not None:
            requete = {"requête": "rapporter", "message": message}
            self.__envoyer(requete)
            self.rapport_envoyee = True

        reponse = self.__recevoir_async()
        if reponse is not None:
            self.rapport_envoyee = False
            return reponse['message']
        else:
            return None

    def protester(self, message):
        """Soulève une exception du type 'Protestation' aux deux joueurs de la partie.
        :param message: Le message de l'exception."""
        requete = {'requête': 'protester', 'message': message}
        self.__envoyer(requete)
        self.__recevoir_sync()  # On reçoit une copie du message envoyé

    def __recevoir_sync(self):
        """Reçoit un message complet de façon synchrone, c'est-à-dire qu'on
        attend qu'un dictionnaire complet ait pu être décodé avant de quitter
        la fonction.
        """
        ret = None
        while ret is None:
            ret = self.__recevoir()
        return ret

    def __recevoir_async(self):
        """Reçoit un message du serveur de jeu façon asynchrone. Si le
        serveur ne renvoit rien, la fonction retourne simplement None.
        """
        self.socket.setblocking(0)
        try:
            reponse = self.__recevoir()
        except socket.error:
            reponse = None
        self.socket.setblocking(1)
        return reponse

    def attack_sent(self):
        ":returns: True or False if attack already sent to other player"
        return self.attaque_envoyee

    def report_sent(self):
        ":returns: True or False if report already sent to other player"
        return self.rapport_envoyee

class EngineBattleShip(ClientReseau):
    """Class that contains the whole engine of the game
    :param sizeWidth: determines the width of the game's window
    :param sizeHeight: determines the height of the game's window"""

    def __init__(self,sizeWidth,sizeHeight):
        self.display = turtle.Screen()
        self.display.setup(sizeWidth,sizeHeight)
        self.username=self.getUserName()
        self.otherplayer=self.getOtherName()
        self.client = ClientReseau(self.username,self.otherplayer)
        self.whilevalue = True
        self.clicturtle = turtle.Turtle()
        self.itemdictionary = {} #initialisation du dictionnaire
        self.turtlekiller = []
        self.x = 0
        self.y = 0
        self.starttime = 0
        self.title = ''
        self.casex = None
        self.casey = None
        self.orientation=True
        self.drawing_turtle=turtle.Turtle()
        self.drawing_turtle.fillcolor("gray")
        self.drawing_turtle.ht()
        self.attackturtle = turtle.Turtle()
        self.attackturtle.hideturtle()
        self.attackturtle.penup()
        self.boatclic = (None,None)
        self.squaresizeatt = 0
        self.squaresizeshot = 0
        self.torpilleur=[]
        self.contre_torpilleur=[]
        self.sous_marin=[]
        self.croiseur=[]
        self.porte_avions=[]
        self.all_position=[]
        self.is_a_boat=False

    def getUserName(self): 
        "Asks the username in a pop up window and sends it to the BattleShip init"
        return self.display.textinput("Your username", "Enter your username : ")
    
    def getOtherName(self): #a ameliorer un peu
        """Function asking enemy username , if nothing is written it will send None"""
        self.otherplayerstring=self.display.textinput("Your enemy", 
         "Enter your enemy username, let blank for a random enemy : ")
        if self.otherplayerstring=='':
            return None
        else:
            return self.otherplayerstring

    def getWhileValue(self):
        """:returns: True or False if the game has started"""
        return self.whilevalue

    def bgImage(self,path):
        "Add a background to the display"
        self.display.bgpic(os.path.abspath(path))

    def button(self,name,path,posx,posy,lenght,height):
        """Create buttons, using images in the game folder. 
        :params: name of the object, image path , X and Y position, width 
        and height of the image in pixels"""
        imageturtle = turtle.Turtle()
        imageturtle.penup()
        imageturtle.goto(posx,posy)
        self.display.addshape(os.path.abspath(path))
        imageturtle.shape(os.path.abspath(path))
        self.itemdictionary[name] = [(lenght,height),(0,0),(0,0),(posx - (lenght/2),posy + (height/2))]

    def startButton(self):
        "Changes the game's state after all the boats are placed"
        if len(self.all_position)==17:
            self.whilevalue = False
        else:
            print('You are not ready to start yet')

    def exitButton(self):
        "Quits the program"
        self.display.bye()

    def protestButton(self):
        """ Button which allows the player to protest and write the complain"""
        self.client.protester(self.display.textinput("Protest", "Complain : "))

    def windowTitleNotification(self,timeToElapse,text1,text2,text3 = None):
        """Sends a notification to the player by changing the name of the window
        :param timeToElapse: set in seconds the time between notifications
        :param text1/text2"""
        timeNow = time.time()
        if (timeNow - self.starttime) >= timeToElapse:
            if self.title == text1:
                self.title = text2
                self.display.title(text2)
            elif self.title == text2:
                if text3 != None:
                    self.title = text3
                    self.display.title(text3)
                else:
                    self.title = text1
                    self.display.title(text1)
            elif self.title == text3:
                self.title = text1
                self.display.title(text1)
            else:
                self.title = text1
                self.display.title(text1)
            self.starttime = time.time()

    def attackPos(self,clicposition):
        "Fonction that returns the position clicked by the player that's attacking"
        temp = self.itemdictionary.get("Up Grid")[0]
        temp2 = self.itemdictionary.get("Up Grid")[1]
        tempposition = self.itemdictionary.get("Up Grid")[3]
        pixelpersquare = temp[0]/temp2[0]
        clicposition2 = clicposition
        for w in range (temp2[0] + 1):
            if clicposition2[0] < ((w * pixelpersquare) + tempposition[0]):
                break
        for h in range (temp2[1] + 1):
            if (clicposition2[1] > (tempposition[1] - (h * pixelpersquare))):
                break
        return((w,h))

    def drawGrid(self,itemName,nbHeight,margin,windowWidth,posX,posY,
                 PengridR,PengridG,PengridB,FillgridR,FillgridG,FillgridB):
        """Fonction that creates a grid. 
        :params: Name of the grid, number of squares in both width and height,
        gap space size for the sides, X and Y position, 
        RBG color for the grid and one for the filling of the squares"""
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
        self.itemdictionary[itemName] = [(windowWidth - 2*margin,windowWidth - 2*margin),(nbHeight,nbHeight),(posX,posY),(rawX,rawY)]

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

    def getGridSquareSize(self,name):
        "Returns the number of squares in width and height of the grid entered"
        stuff = self.itemdictionary.get(name)[1]
        return(stuff[0])

    def clicManager(self):
        """Detects the clicks of the user and returns the name of the object 
        that the user clicked.
        :returns: (key,(posX,posY)) where key is the item name and 
        posX and posY are raw coordinates."""
        self.turtlekiller.append(self.clicturtle)
        victimTurtle = self.turtlekiller[0]
        victimTurtle._tracer(10,1000)
        victimTurtle.penup()
        victimTurtle.hideturtle()
        self.display.onscreenclick(victimTurtle.goto)
        posX = victimTurtle.position()[0]
        posY = victimTurtle.position()[1]
        if posX != 0.00 and posY != 0.00:
            for key in self.itemdictionary:
                temp = self.itemdictionary.get(key)[0]
                lenght = temp[0]
                height = temp[1]
                temp = self.itemdictionary.get(key)[3]
                posXItem = temp[0]
                posYItem = temp[1]
                if (posX >= posXItem and posX <= posXItem + lenght) and (posYItem >= posY and posY >= posYItem - height):
                    self.clicturtle.goto(0,0)
                    return((key,(posX,posY)))
        self.turtlekiller.clear()

    def gridDecomposer(self,name,clicPosition): 
        """Returns the raw X and Y position of the top left square 
        corner clicked by the user.
        :param: name is the name of the grid.
        :param: clicPosition is (key,(posX,posY)) where key is the item 
        name and posX and posY are raw coordinates.
        :returns: (positionX,positionY) where positionX and positionY 
        are raw X and Y position of the top left square corner."""
        for key in self.itemdictionary:
            if key == name:
                temp = self.itemdictionary.get(key)[0]
                temp2 = self.itemdictionary.get(key)[1]
                tempPosition = self.itemdictionary.get(key)[3]
                pixelPerSquare = temp[0]/temp2[0]
                clicPosition2 = clicPosition[1]
                for x in range (temp2[0] + 1):
                    if clicPosition2[0] < ((x * pixelPerSquare) + tempPosition[0]):
                        self.casex = x
                        break
                for y in range (temp2[1] + 1):
                    if (clicPosition2[1] > (tempPosition[1] - (y * pixelPerSquare))):
                        self.casey = y
                        break
        positionX = ((x -1) * pixelPerSquare) + tempPosition[0]
        positionY = tempPosition[1] - ((y - 1) * pixelPerSquare)
        return (positionX,positionY)

    def getClickedSquare(self):
        ''' Get case number from the grid 
        :returns: (casex, casey) a tuple which identifies the case 
        between 0 and 9.'''
        if self.casex != None and self.casey != None:
            transitionX = self.casex
            transitionY = self.casey
            self.casex = None
            self.casey = None
            return ((transitionX-1,transitionY-1))
    
    def itemDetector(self,clicPosition,attaqueEnvoyee=None):
        '''Treats items which are in itemdictionnary
        :param clicPosition is (key,(posX,posY)) where key is the item 
        name and posX and posY are raw coordinates.
        :returns: nothing'''
        if (clicPosition != None):
            for key in self.itemdictionary:
                if (key == clicPosition[0]):
                    shortcut = self.itemdictionary.get(key)
                    if (shortcut[1] != (0,0)):
                        self.gridDecomposer(key,clicPosition) 
                        self.squaresizeatt = self.getGridSquareSize("Down Grid")
                        self.squaresizeshot = self.getGridSquareSize("Up Grid")
                        if key == "Up Grid" and self.getWhileValue() != True and attaqueEnvoyee != True: 
                            self.attackturtle.goto(self.gridDecomposer("Up Grid",clicPosition))
                            self.attackedSquare = self.getClickedSquare()
                            self.attackturtle.pencolor('white')
                            self.attackturtle.begin_fill()
                            correction = 4
                            self.attackturtle.goto(self.attackturtle.pos()[0] + self.squaresizeshot * 2 + correction,self.attackturtle.pos()[1])
                            self.attackturtle.goto(self.attackturtle.pos()[0],self.attackturtle.pos()[1] - self.squaresizeshot * 2 - correction)
                            self.attackturtle.goto(self.attackturtle.pos()[0] - self.squaresizeshot * 2 - correction, self.attackturtle.pos()[1])
                            self.attackturtle.goto(self.attackturtle.pos()[0],self.attackturtle.pos()[1] + self.squaresizeshot * 2 + correction)
                            self.attackturtle.end_fill()
                            tempPosX = self.attackPos(self.attackturtle.pos())[0] - 1
                            tempPosY = self.attackPos(self.attackturtle.pos())[1] - 1
                            self.client.attaquer((tempPosX,tempPosY))

                        if self.boatclic != (None,None):
                            if key != "Up Grid" and self.getWhileValue() == True: 
                                self.boatButton(self.gridDecomposer(key,clicPosition))
                                self.boatclic = (None,None)
                    elif (shortcut[1] == (0,0)):
                        if key == "start":
                            self.startButton() #a supprimer et decommenter le reste du if
                            #if len(self.all_position)!=17:
                            #    print('You still have some inactives ships')
                            #else:
                            #    self.startButton()
                        elif key == "exit":
                            self.exitButton()
                        elif key == "infos":
                            self.protestButton()
                        elif (key=="porte-avions") or (key=="contre-torpilleur") or (key=="sous-marin") or (key=="croiseur") or (key=="torpilleur"):
                            self.boat(key)
                            self.orientation=True

    def boatVertical(self):
        ''' Allows to place vertical boats using right arrow '''
        if self.getWhileValue()==True:
            self.display.onkeypress(None,'Right')
            self.orientation=True
            self.display.onkeypress(self.boatVertical,'Right')
            print("The boat is vertical")

    def boatHorizontal(self):
        ''' Allows to place horizontal boats using left arrow'''
        if self.getWhileValue()==True:
            self.display.onkeypress(None,'Left')
            self.orientation=False
            self.display.onkeypress(self.boatHorizontal,'Left')
            print("The boat is horizontal")


    def boatButton(self,position):
        '''Function which allows the click following the click on an 
        icon boat to place the boat in the grid '''
        squarePosition=self.getClickedSquare()
        self.isThereABoat(squarePosition)
        if squarePosition != (None,None):
            for i in range (self.boatclic[0]):
                if self.orientation==True:
                    self.square_size = 38
                    self.drawing_turtle.penup
                    self.color_x=position[0]
                    self.color_y=position[1]-self.square_size*i
                    self.testv=position[1]-self.square_size*(self.boatclic[0]-1)
                    self.testh=position[0]-self.square_size*(self.boatclic[0]-1)
                    if self.testv>=-302 and self.is_a_boat==False:
                        self.drawing_turtle.penup()
                        self.drawing_turtle.goto(self.color_x,self.color_y)
                        self.drawing_turtle.pendown()
                        self.drawing_turtle.begin_fill()
                        self.drawing_turtle.goto(self.color_x+self.square_size,
                                                 self.color_y)
                        self.drawing_turtle.goto(self.color_x+self.square_size,
                                                 self.color_y-self.square_size)
                        self.drawing_turtle.goto(self.color_x,
                                                 self.color_y-self.square_size)
                        self.drawing_turtle.goto(self.color_x,self.color_y)
                        self.drawing_turtle.end_fill()        
                else:
                    self.square_size = 38
                    self.drawing_turtle.penup()
                    self.color_x=position[0]+self.square_size*i
                    self.color_y=position[1]
                    self.testh=position[0]+self.square_size*(self.boatclic[0]-1)
                    if self.testh <= 152 and self.is_a_boat==False:
                        self.drawing_turtle.penup()
                        self.drawing_turtle.goto(self.color_x,self.color_y)
                        self.drawing_turtle.pendown()
                        self.drawing_turtle.begin_fill()
                        self.drawing_turtle.goto(self.color_x+self.square_size,
                                                 self.color_y)
                        self.drawing_turtle.goto(self.color_x+self.square_size,
                                                 self.color_y-self.square_size)
                        self.drawing_turtle.goto(self.color_x,
                                                 self.color_y-self.square_size)
                        self.drawing_turtle.goto(self.color_x,self.color_y)
                        self.drawing_turtle.end_fill()
            self.BoatDict(squarePosition)

    def boat(self,key):
        "Allows the program to differentiate which boat is placed on the grid"
        if key == "sous-marin":
            if self.sous_marin==[]:
                self.boatclic = (3,"sous-marin")
            else:
                print("This ship is already on the map")
        elif key == "contre-torpilleur":
            if self.contre_torpilleur==[]:
                self.boatclic = (3,"contre-torpilleur")
            else:
                print("This ship is already on the map")
        elif key =="porte-avions":
            if self.porte_avions==[]:
                self.boatclic = (5,"porte-avions")
            else:
                print("This ship is already on the map")
        elif key =="torpilleur":
            if self.torpilleur==[]:
                self.boatclic = (2,"torpilleur")
            else:
                print("This ship is already on the map")
        elif key =="croiseur":
            if self.croiseur==[]:
              self.boatclic = (4,"croiseur")
            else:
                print("This ship is already on the map")
        
    def BoatDict(self, position):
        ''' Add ships position in a liste '''
        self.squarePosition=position
        self.isThereABoat(self.squarePosition)
        if self.boatclic==(3,"sous-marin"):
            if self.orientation==True:
                if self.testv>=-302 and self.is_a_boat==False:
                    for i in range (self.boatclic[0]):
                            self.sous_marin.append((position[0],position[1]+i))
                            self.all_position.append((position[0],position[1]+i))
            else:
                if self.testh <= 152 and self.is_a_boat==False:
                    for i in range (self.boatclic[0]):
                        self.sous_marin.append((position[0]+i,position[1]))
                        self.all_position.append((position[0]+i,position[1]))


        if self.boatclic==(2,"torpilleur"):
            if self.orientation==True:
                if self.testv>=-302 and self.is_a_boat==False:
                    for i in range (self.boatclic[0]):
                        self.torpilleur.append((position[0],position[1]+i))
                        self.all_position.append((position[0],position[1]+i))
            else:
                if self.testh <= 152 and self.is_a_boat==False:
                    for i in range (self.boatclic[0]):
                        self.torpilleur.append((position[0]+i,position[1])) 
                        self.all_position.append((position[0]+i,position[1]))
        
        if self.boatclic==(3,"contre-torpilleur"):
            if self.orientation==True:
                if self.testv>=-302 and self.is_a_boat==False:
                    for i in range (self.boatclic[0]):
                        self.contre_torpilleur.append((position[0],position[1]+i))
                        self.all_position.append((position[0],position[1]+i))
            else:
                if self.testh <= 152 and self.is_a_boat==False:
                    for i in range (self.boatclic[0]):
                        self.contre_torpilleur.append((position[0]+i,position[1])) 
                        self.all_position.append((position[0]+i,position[1]))
                        print(self.all_position) 


        if self.boatclic==(5,"porte-avions"):
            if self.orientation==True:
                if self.testv>=-302 and self.is_a_boat==False:
                    for i in range (self.boatclic[0]):
                        self.porte_avions.append((position[0],position[1]+i))
                        self.all_position.append((position[0],position[1]+i))
            else:
                if self.testh<=152 and self.is_a_boat==False:
                    for i in range (self.boatclic[0]):
                        self.porte_avions.append((position[0]+i,position[1]))
                        self.all_position.append((position[0]+i,position[1])) 
                       
        if self.boatclic==(4,"croiseur"):
            if self.orientation==True:
                if self.testv>=-302 and self.is_a_boat==False:
                    for i in range (self.boatclic[0]):
                        self.croiseur.append((position[0],position[1]+i))
                        self.all_position.append((position[0],position[1]+i))
            else:
                if self.testh<=152 and self.is_a_boat==False:    
                    for i in range (self.boatclic[0]):
                        self.croiseur.append((position[0]+i,position[1]))
                        self.all_position.append((position[0]+i,position[1])) 


    def isThereABoat(self, position):
        ''' Function that checks if the position where the player want to 
        place his ship is already used by another ship. 
        It prevents boat stacking '''
        if self.boatclic==(3,"sous-marin") or self.boatclic==(3,"contre-torpilleur"):
            if self.orientation==True:
                if (position[0],position[1]) in self.all_position or (position[0],position[1]+1) in self.all_position or (position[0],position[1]+2) in self.all_position:
                    self.is_a_boat=True
                else:
                    self.is_a_boat=False

            elif self.orientation==False:
                if (position[0],position[1]) in self.all_position or (position[0]+1,position[1]) in self.all_position or (position[0]+2,position[1]) in self.all_position:
                    self.is_a_boat=True
                else:
                    self.is_a_boat=False
        
        if self.boatclic==(2,"torpilleur"):
            if self.orientation==True:
                if (position[0],position[1]) in self.all_position or (position[0],position[1]+1) in self.all_position:
                    self.is_a_boat=True
                else:
                    self.is_a_boat=False

            elif self.orientation==False:
                if (position[0],position[1]) in self.all_position or (position[0]+1,position[1]) in self.all_position:
                    self.is_a_boat=True
                else:
                    self.is_a_boat=False

            if self.orientation==False:
                if (position[0],position[1]) in self.all_position or (position[0]+1,position[1]) in self.all_position:
                    self.is_a_boat=True
                else:
                    self.is_a_boat=False

        if self.boatclic==(4,"croiseur"):
            if self.orientation==True:
                if (position[0],position[1]) in self.all_position or (position[0],position[1]+1) in self.all_position or (position[0],position[1]+2) in self.all_position or (position[0],position[1]+3) in self.all_position:
                    self.is_a_boat=True
                else:
                    self.is_a_boat=False

            elif self.orientation==False:
                if (position[0],position[1]) in self.all_position or (position[0]+1,position[1]) in self.all_position or (position[0]+2,position[1]) in self.all_position or (position[0],position[1]+3) in self.all_position:
                    self.is_a_boat=True
                else:
                    self.is_a_boat=False

        if self.boatclic==(3,"porte-avions"):
            if self.orientation==True:
                if (position[0],position[1]) in self.all_position or (position[0],position[1]+1) in self.all_position or (position[0],position[1]+2) in self.all_position or (position[0],position[1]+3) in self.all_position or (position[0],position[1]+4) in self.all_position:
                    self.is_a_boat=True
                else:
                    self.is_a_boat=False

            elif self.orientation==False:
                if (position[0],position[1]) in self.all_position or (position[0]+1,position[1]) in self.all_position or (position[0]+2,position[1]) in self.all_position or (position[0],position[1]+3) in self.all_position or (position[0],position[1]+4) in self.all_position:
                    self.is_a_boat=True
                else:
                    self.is_a_boat=False

        if self.boatclic==(3,"porte-avions"):
            if self.orientation==True:
                if (position[0],position[1]) in self.all_position or (position[0],position[1]+1) in self.all_position or (position[0],position[1]+2) in self.all_position or (position[0],position[1]+3) in self.all_position or (position[0],position[1]+4) in self.all_position:
                    self.is_a_boat=True
                else:
                    self.is_a_boat=False

            elif self.orientation==False:
                if (position[0],position[1]) in self.all_position or (position[0]+1,position[1]) in self.all_position or (position[0]+2,position[1]) in self.all_position or (position[0],position[1]+3) in self.all_position or (position[0],position[1]+4) in self.all_position:
                    self.is_a_boat=True
                else:
                    self.is_a_boat=False
    
    def damage(self, attack):
        ''' Function that treats the attack results and sends them to the other player
        :param attack: a tuple (x,y) which are grid coordinates between 0 and 9'''
        if attack in self.torpilleur: #-------torpilleur
            self.torpilleur.remove(attack)
            self.all_position.remove(attack)
            if self.torpilleur == [] and self.all_position!=[]:
                self.client.rapporter('Hit and Sank')
            elif self.torpilleur ==[] and self.all_position==[]:
                self.client.rapporter('Win')
                self.loseAnim()
            else:
                self.client.rapporter('Hit')
        elif attack in self.contre_torpilleur:
            self.contre_torpilleur.remove(attack)
            self.all_position.remove(attack)
            if self.contre_torpilleur == [] and self.all_position!=[]:
                self.client.rapporter('Ht and sank')
            elif self.contre_torpilleur ==[] and self.all_position==[]:
                self.client.rapporter('Win')
                self.loseAnim()
            else:
                self.client.rapporter('Hit')
        elif attack in self.croiseur:
            self.croiseur.remove(attack)
            self.all_position.remove(attack)
            if self.croiseur == [] and self.all_position!=[]:
                self.client.rapporter('Hit and Sank')
            elif self.croiseur ==[] and self.all_position==[]:
                self.client.rapporter('Win')
                self.loseAnim()
            else:
                self.client.rapporter('Hit and sank')
        elif attack in self.porte_avions:
            self.porte_avions.remove(attack)
            self.all_position.remove(attack)
            if self.porte_avions == [] and self.all_position!=[]:
                self.client.rapporter('Hit and Sank')
            elif self.porte_avions ==[] and self.all_position==[]:
                self.client.rapporter('Win')
                self.loseAnim()
            else:
                self.client.rapporter('Hit')
        elif attack in self.sous_marin:
            self.sous_marin.remove(attack)
            self.all_position.remove(attack)
            if self.sous_marin == [] and self.all_position!=[]:
                self.client.rapporter('Hit and sank')
            elif self.sous_marin ==[] and self.all_position==[]:
                self.client.rapporter('Win')
                self.loseAnim()
            else:
                self.client.rapporter('Hit')
        else:
            self.client.rapporter("Miss")
        print(self.all_position)

    def winAnim(self,report):
        ''' Creates a win animation at the end of the game '''
        if report=='Win':
            self.Win_turtle=turtle.Turtle()
            self.Win_turtle.ht()
            self.Win_turtle.color('red')
            self.Win_turtle.pensize(400)
            self.Win_turtle.penup()
            self.Win_turtle.goto(-200,200)
            self.Win_turtle.pendown()
            self.Win_turtle.goto(200,200)
            self.Win_turtle.goto(200,-200)
            self.Win_turtle.goto(-200,-200)
            self.Win_turtle.penup()
            self.Win_turtle.goto(-400,0)
            self.Win_turtle.color('white')
            self.Win_turtle.write('Victory!', move=False, 
                                  align="left", font=("Arial", 180, "normal"))

    def loseAnim(self):
        '''Create a lose animation at the end of the game '''
        self.Win_turtle=turtle.Turtle()
        self.Win_turtle.ht()
        self.Win_turtle.color('black')
        self.Win_turtle.pensize(400)
        self.Win_turtle.penup()
        self.Win_turtle.goto(-200,200)
        self.Win_turtle.pendown()
        self.Win_turtle.goto(200,200)
        self.Win_turtle.goto(200,-200)
        self.Win_turtle.goto(-200,-200)
        self.Win_turtle.penup()
        self.Win_turtle.goto(-400,0)
        self.Win_turtle.color('white')
        self.Win_turtle.write('Defeat!', move=False, align="left", 
                              font=("Arial", 180, "normal"))
    
    def squarePixelPos(self,name,tupleSquarePos): 
        ''' Returns the position in pixels of a selected square in a grid.
        :params: name of the grid and the position inside that grid 
        of the designed square.
        :returns: a tuple of the position in pixels.'''
        for key in self.itemdictionary:
            if key == name:
                temp = self.itemdictionary.get(key)[0]
                temp2 = self.itemdictionary.get(key)[1]
                tempPosition = self.itemdictionary.get(key)[3]
                pixelPerSquare = temp[0]/temp2[0]
                tempPositionX = tupleSquarePos[0]*pixelPerSquare+tempPosition[0]
                tempPositionY = tempPosition[1] - (tupleSquarePos[1]*pixelPerSquare)
        return (tempPositionX,tempPositionY)

    def attackColor(self,attack,tuple):
        """colours the attacked case in the lower grid
        :param attack: x and y coordinates in pixels of the case
        :param tuple: tuple of coordinates of the case (between 0 and 9)"""
        A_colorx=attack[0]
        A_colory=attack[1]
        if tuple in self.all_position:
            self.drawing_turtle.fillcolor('red')
            self.drawing_turtle.penup()
            self.drawing_turtle.goto(A_colorx,A_colory)
            self.drawing_turtle.pendown()
            self.drawing_turtle.begin_fill()
            self.drawing_turtle.goto(A_colorx+38,A_colory)
            self.drawing_turtle.goto(A_colorx+38,A_colory-38)
            self.drawing_turtle.goto(A_colorx,A_colory-38)
            self.drawing_turtle.goto(A_colorx,A_colory)
            self.drawing_turtle.end_fill()
        else:
            self.drawing_turtle.fillcolor('white')
            self.drawing_turtle.penup()
            self.drawing_turtle.goto(A_colorx,A_colory)
            self.drawing_turtle.pendown()
            self.drawing_turtle.begin_fill()
            self.drawing_turtle.goto(A_colorx+38,A_colory)
            self.drawing_turtle.goto(A_colorx+38,A_colory-38)
            self.drawing_turtle.goto(A_colorx,A_colory-38)
            self.drawing_turtle.goto(A_colorx,A_colory)
            self.drawing_turtle.end_fill()


def main():
    parser = argparse.ArgumentParser(prog="BattleShip : The Space Battle")
    parser.add_argument('playername', help='First Player', default="player one")
    parser.add_argument('othername', help='First Player', default=None)

    try:
        args = parser.parse_args()
        game = EngineBattleShip(800,800, args.playername, args.othername)
    except:
        game = EngineBattleShip(800,800)

    os.system('cls')

    game.bgImage("image\\Background.gif")

    #Grids
    game.drawGrid("Down Grid",10,10,400,200,350,0,0,0,102,102,255)
    game.drawGrid("Up Grid",10,10,250,275,75,0,0,0,102,102,255)

    #Buttons
    game.button('start',"image\\gifButtons\\start.gif",-330,330,150,150)
    game.button("infos","image\\gifButtons\\Credits.gif",-350,-340,80,80)
    game.button("exit","image\\gifButtons\\exit.gif",330,340,100,100)
    game.button("torpilleur","image\\gifButtons\\boat2.gif",-350,50,67,25)
    game.button("contre-torpilleur","image\\gifButtons\\boat3a.gif",-350,0,99,29)
    game.button("sous-marin","image\\gifButtons\\boat3b.gif",-350,-50,105,29)
    game.button("croiseur","image\\gifButtons\\boat4.gif",-325,-100,147,31)
    game.button("porte-avions","image\\gifButtons\\boat5.gif",-322,-150,177,41)
    
    #Main loops
    print(game.contre_torpilleur, game.torpilleur, game.croiseur,
          game.porte_avions, "all position:", game.all_position)
    starttimeResponse = time.time()
    while game.getWhileValue():
        #Initial window title
        game.windowTitleNotification(3,"Welcome to BattleShip : The Space Battle",
                                     "Please place your ships")
        game.itemDetector(game.clicManager())
        game.display.onkeypress(game.boatVertical,'Right')
        game.display.onkeypress(game.boatHorizontal,'Left')
        game.display.listen()
    print("You have now started the game")
    print("You are playing against : " + str(game.client.adversaire()))
    while True:
        #Actual gameplay
        tempClient=None
        while tempClient == None: #loop waiting for attack results
            game.itemDetector(game.clicManager(),game.client.attack_sent())
            timeNow3 = time.time()
            if (timeNow3 - starttimeResponse) >= 0.1:
                tempClient = game.client.attaquer()
                starttimeResponse =  time.time()
                if tempClient != None:
                    print(tempClient)
                    break
        tempClient2=(tempClient[0],tempClient[1])
        game.attackColor(game.squarePixelPos('Down Grid',
                                             tempClient2),tempClient2)
        game.damage(tempClient2)
        rapporter = None
        while rapporter == None: # loop waiting for the opponent's response
            timeNow3 = time.time()
            if (timeNow3-starttimeResponse) >= 0.1:
                rapporter = game.client.rapporter()
                starttimeResponse = time.time()
                if rapporter != None:
                    game.winAnim(rapporter)
                    print(rapporter)
                    break

if __name__ == "__main__":
    main()