# Welcome and have fun programming!
# Project by Damien Arroyo, William and Nadia.
# AWESOME !

# -*- coding: utf-8 -*-

import json, socket, time, turtle, os, webbrowser, argparse, sys

class Protestation(Exception):
    pass

class ClientReseau(object): #ClientReseau(pseudo, adversaire=None, serveur='python.gel.ulaval.ca', port=31415)
    """Client réseau pour jeu en-ligne.
    :param pseudo: votre pseudonyme.
    :param adversaire: le pseudonyme de l'adversaire que vous désirez affronter, None fera un pairage aléatoire.
    :param serveur: l'adresse ou le nom de l'hôte du serveur de jeu.
    :param port: le port du serveur de jeu."""

    def __init__(self, pseudo, adversaire, serveur='python.gel.ulaval.ca', port=31415):
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
        requete = {"requête": "créer", "pseudo": self.pseudo, "adversaire": self.adv}
        self.__envoyer(requete)
        return self.__recevoir_sync()

    def __envoyer(self, requete):
        """Envoie une requête au serveur de jeu sous la forme d'une chaîne
        de caractères JSON.
        """
        self.socket.sendall(bytes("\x02" + json.dumps(requete) + "\x03", "utf-8"))

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
        """Transmet au serveur la cellule de votre attaque. Cette cellule est constituée d'un
        tuple de deux indices compris entre 0 et 9.
        
        :param cellule: La cellule à attaquer sous la forme d'un tuple de deux indices compris
        entre 0 et 9. Pour vérifier si la réponse de l'adversaire est arriver, il faut mettre l'argument à None.
        :return: La cellule attaquée par votre adversaire si celle-ci est disponible; None autrement.

        Cette fonction retourne None si aucune réponse de votre adversaire n'a été obtenue
        à temps par le serveur de jeu. Dans ce cas, vous devez rappeler la fonction sans argument
        jusqu'à ce vous obteniez une réponse (de préférence, introduire un délai entre les appels)."""
        assert cellule is None or self.attaque_envoyee == False, ("Vous devez attendre la réponse"
                                                                  "avant d'envoyer une nouvelle"
                                                                  "attaque")
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
        """Rapporte au serveur le message du résultat de la dernière attaque de votre adversaire.

        :param message: la chaîne de caractères de votre rapport.
        :returns: Le rapport de votre adversaire s'il est disponible; None autrement.

        Cette fonction retourne None si aucune réponse de votre adversaire n'a été obtenue
        à temps par le serveur de jeu. Dans ce cas, vous devez rappeler la fonction sans argument
        jusqu'à ce vous obteniez une réponse (de préférence, introduire un délai entre les appels).
        """
        assert message is None or not self.attaque_envoyee, ("Vous devez attendre la réponse"
                                                             " avant d'envoyer un nouveau"
                                                             " rapport")
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

class engineBattleShip(ClientReseau):
    "Class that contains the whole engine of the game"
    def __init__(self,sizeWidth,sizeHeight):
        self.display = turtle.Screen()
        self.display.setup(sizeWidth,sizeHeight)
        self.username=self.GetUserName()
        self.otherplayer=self.GetOtherName()
        self.client = ClientReseau(self.username,self.otherplayer)
        self.whileValue = True
        self.clicTurtle = turtle.Turtle()
        self.itemdictionary = {} #initialisation du dictionnaire
        self.turtlekiller = []
        self.x = 0
        self.y = 0
        self.startTime = 0
        self.title = ''
        self.caseX = None
        self.caseY = None
        self.orientation=True
        self.drawing_turtle=turtle.Turtle()
        self.drawing_turtle.fillcolor("gray")
        self.drawing_turtle.ht()
        self.attackTurtle = turtle.Turtle()
        self.attackTurtle.hideturtle()
        self.attackTurtle.penup()
        self.boatClic = (None,None)
        self.squareSizeAtt = 0
        self.squareSizeShot = 0
        self.torpilleur=[]
        self.contre_torpilleur=[]
        self.sous_marin=[]
        self.croiseur=[]
        self.porte_avions=[]
        self.all_position=[]
        self.is_a_boat=False
        self.secondTime = 0

    def GetUserName(self): 
        "Function asking your username and send it to the BattleShip init"
        return self.display.textinput("Your username", "Enter your username : ")
    
    def GetOtherName(self): #a ameliorer un peu
        "Function asking your enemy username and send it to the BattleShip init, if nothing is written it will send None"
        self.otherplayerstring=self.display.textinput("Your enemy", "Enter your enemy username, let blank for a random enemy : ")
        if self.otherplayerstring=='':
            return None
        else:
            return self.otherplayerstring

    def Clear(self):
        "Clear the display"
        self.display.clear()

    def GetWhileValue(self):
        return self.whileValue

    def BgImage(self,path):
        "Add a background to the display"
        self.display.bgpic(os.path.abspath(path))

    def Button(self,name,path,posX,posY,lenght,height): #not 100% good yet
        "Create buttons, using images in the game folder. Needs: name of the object, image path , X and Y position, width and height of the image in pixels"
        imageTurtle = turtle.Turtle()
        imageTurtle.penup()
        imageTurtle.goto(posX,posY)
        self.display.addshape(os.path.abspath(path))
        imageTurtle.shape(os.path.abspath(path))
        #[(windowWidth - 2*margin,windowWidth - 2*margin),(nbHeight,nbHeight),(posX,posY),(rawX,rawY)]
        self.itemdictionary[name] = [(lenght,height),(0,0),(0,0),(posX - (lenght/2),posY + (height/2))]

    def StartButton(self):
        "Changes the part of the game the player is in"
        self.whileValue = False

    def ExitButton(self):
        "Quits the program"
        self.display.bye()

    def InfoButton(self):
        self.client.protester(self.display.textinput("Protest", "Complain : "))

    def WindowTitleNotification(self,timeToElapse,text1,text2,text3 = None):
        """Sends a notification to the player by changing the name of the window
        :param timeToElapse: set in seconds the time between notifications
        :param text1/text2"""
        timeNow = time.time()
        if (timeNow - self.startTime) >= timeToElapse:
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
            self.startTime = time.time()

    def AttackPos(self,clicPosition):
        "Fonction that returns the position clicked by the player that's attacking"
        name = "Up Grid"
        key = name
        temp = self.itemdictionary.get(key)[0]
        temp2 = self.itemdictionary.get(key)[1]
        tempPosition = self.itemdictionary.get(key)[3]
        pixelPerSquare = temp[0]/temp2[0]
        clicPosition2 = clicPosition
        for w in range (temp2[0] + 1):
            if clicPosition2[0] < ((w * pixelPerSquare) + tempPosition[0]):
                break
        for h in range (temp2[1] + 1):
            if (clicPosition2[1] > (tempPosition[1] - (h * pixelPerSquare))):
                break
        return((w,h))

    def DrawGrid(self,itemName,nbHeight,margin,windowWidth,posX,posY,PengridR,PengridG,PengridB,FillgridR,FillgridG,FillgridB):
        "Fonction that creates a grid. Requires : Name of the grid, numbre of squares in both width and height, gap space size for the sides, X and Y position, RBG color for the grid and one for the filling of the squares"
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


    def GetRawItemPosition(self,name):
       "Returns the position of the specified item"
       return(self.itemdictionary.get(name)[3])

    def GetGridSquareSize(self,name):
        "Returns the number of squares in width and height of the grid entered (Same number of squares both ways)"
        stuff = self.itemdictionary.get(name)[1]
        return(stuff[0])
    

    def GetItemSize(self,name):
        "Returns the size of the specified item in a tuple"
        return(self.itemdictionary.get(name)[0])


    def ClicManager(self):
        """Detects the clicks of the user and returns the name of the object that the user clicked
        :returns: (key,(posX,posY)) where key is the item name and posX and posY are raw coordinates"""
        self.turtlekiller.append(self.clicTurtle)
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
                    self.clicTurtle.goto(0,0)
                    return((key,(posX,posY)))
        self.turtlekiller.clear()

    def GridDecomposer(self,name,clicPosition): #c'est quoi le parametre name??
        """Returns the raw X and Y position of the top left square corner clicked by the user
        :param: name is the name of the grid
        :param: clicPosition is (key,(posX,posY)) where key is the item name and posX and posY are raw coordinates
        :returns: (positionX,positionY) where positionX and positionY 
                                   are raw X and Y position of the top left square corner"""
        for key in self.itemdictionary:
            if key == name:
                temp = self.itemdictionary.get(key)[0]
                temp2 = self.itemdictionary.get(key)[1]
                tempPosition = self.itemdictionary.get(key)[3]
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
        return (positionX,positionY)

    def GetClickedSquare(self):
        ''' Get case number from the grid 
        :returns: (caseX, caseY) a tuple which identifies the case between 0 and 9 '''
        if self.caseX != None and self.caseY != None:
            transitionX = self.caseX
            transitionY = self.caseY
            self.caseX = None
            self.caseY = None
            return ((transitionX-1,transitionY-1))
    
    def ItemDetector(self,clicPosition,attaqueEnvoyee=None): #attaqueEnvoyee prend attaque_envoyee de ClientReseau
        '''Treats items which are in itemdictionnary
        :param clicPosition is (key,(posX,posY)) where key is the item name and posX and posY are raw coordinates
        :returns: nothing'''
        if (clicPosition != None):
            for key in self.itemdictionary:
                if (key == clicPosition[0]):
                    shortcut = self.itemdictionary.get(key)
                    if (shortcut[1] != (0,0)):
                        self.GridDecomposer(key,clicPosition) # Si c'est une grid execute le programme qui renvoit la coordonée de la case
                        self.squareSizeAtt = self.GetGridSquareSize("Down Grid")
                        self.squareSizeShot = self.GetGridSquareSize("Up Grid")
                        if key == "Up Grid" and self.GetWhileValue() != True and attaqueEnvoyee != True: #coloriage de la case attaquée sur la grille d'en haut
                            self.attackTurtle.goto(self.GridDecomposer("Up Grid",clicPosition))
                            self.attackedSquare = self.GetClickedSquare()
                            self.attackTurtle.begin_fill()
                            correction = 4
                            self.attackTurtle.goto(self.attackTurtle.pos()[0] + self.squareSizeShot * 2 + correction,self.attackTurtle.pos()[1])
                            self.attackTurtle.goto(self.attackTurtle.pos()[0],self.attackTurtle.pos()[1] - self.squareSizeShot * 2 - correction)
                            self.attackTurtle.goto(self.attackTurtle.pos()[0] - self.squareSizeShot * 2 - correction, self.attackTurtle.pos()[1])
                            self.attackTurtle.goto(self.attackTurtle.pos()[0],self.attackTurtle.pos()[1] + self.squareSizeShot * 2 + correction)
                            self.attackTurtle.end_fill()
                            tempPosX = self.AttackPos(self.attackTurtle.pos())[0] - 1
                            tempPosY = self.AttackPos(self.attackTurtle.pos())[1] - 1
                            self.client.attaquer((tempPosX,tempPosY))

                        if self.boatClic != (None,None): #si on a selectionne un bateau alors on peut le placer dans la grille du bas
                            if key != "Up Grid" and self.GetWhileValue() == True: #si on est pas sur la grille du haut et on est dans la loop avant Start
                                self.BoatButton(self.GridDecomposer(key,clicPosition))
                                self.boatClic = (None,None)
                    elif (shortcut[1] == (0,0)):
                        if key == "start":
                            self.StartButton() #a supprimer et decommenter le reste du if
                            #if len(self.all_position)!=17:
                            #    print('You still have some inactives ships')
                            #else:
                            #    self.StartButton()
                        elif key == "exit":
                            self.ExitButton()
                        elif key == "infos":
                            self.InfoButton()
                        elif (key=="porte-avions") or (key=="contre-torpilleur") or (key=="sous-marin") or (key=="croiseur") or (key=="torpilleur"):
                            self.Boat(key)
                            self.orientation=True

    def BoatVertical(self):
        ''' Permet de placer les bateaux à la verticale avec la flèche de droite '''
        if self.GetWhileValue()==True:
            self.display.onkeypress(None,'Right')
            self.orientation=True
            self.display.onkeypress(self.BoatVertical,'Right')
            print("The boat is vertical")

    def BoatHorizontal(self):
        ''' Permet de placer les bateaux à l'horizontale avec la flèche de gauche '''
        if self.GetWhileValue()==True:
            self.display.onkeypress(None,'Left')
            self.orientation=False
            self.display.onkeypress(self.BoatHorizontal,'Left')
            print("The boat is horizontal")


    def BoatButton(self,position):
        ''' Fonction qui permet au click suivant le click sur une icone bateau de placer le bateau dans la grille '''
        squarePosition=self.GetClickedSquare()
        self.IsThereABoat(squarePosition)
        if squarePosition != (None,None):
            for i in range (self.boatClic[0]):
                if self.orientation==True:
                    self.square_size = 38
                    self.drawing_turtle.penup
                    self.color_x=position[0]
                    self.color_y=position[1]-self.square_size*i
                    self.testv=position[1]-self.square_size*(self.boatClic[0]-1)
                    self.testh=position[0]-self.square_size*(self.boatClic[0]-1)
                    if self.testv>=-302 and self.is_a_boat==False:
                        self.drawing_turtle.penup()
                        self.drawing_turtle.goto(self.color_x,self.color_y)
                        self.drawing_turtle.pendown()
                        self.drawing_turtle.begin_fill()
                        self.drawing_turtle.goto(self.color_x+self.square_size,self.color_y)
                        self.drawing_turtle.goto(self.color_x+self.square_size,self.color_y-self.square_size)
                        self.drawing_turtle.goto(self.color_x,self.color_y-self.square_size)
                        self.drawing_turtle.goto(self.color_x,self.color_y)
                        self.drawing_turtle.end_fill()        
                else:
                    self.square_size = 38
                    self.drawing_turtle.penup()
                    self.color_x=position[0]+self.square_size*i
                    self.color_y=position[1]
                    self.testh=position[0]+self.square_size*(self.boatClic[0]-1)
                    if self.testh <= 152 and self.is_a_boat==False:
                        self.drawing_turtle.penup()
                        self.drawing_turtle.goto(self.color_x,self.color_y)
                        self.drawing_turtle.pendown()
                        self.drawing_turtle.begin_fill()
                        self.drawing_turtle.goto(self.color_x+self.square_size,self.color_y)
                        self.drawing_turtle.goto(self.color_x+self.square_size,self.color_y-self.square_size)
                        self.drawing_turtle.goto(self.color_x,self.color_y-self.square_size)
                        self.drawing_turtle.goto(self.color_x,self.color_y)
                        self.drawing_turtle.end_fill()
            self.BoatDict(squarePosition)

    def Boat(self,key):
        ''' Permet au programme de différencier quel bateau est placé sur la grille suite au clique '''
        if key == "sous-marin":
            if self.sous_marin==[]:
                self.boatClic = (3,"sous-marin")
            else:
                print("This ship is already on the map")
        elif key == "contre-torpilleur":
            if self.contre_torpilleur==[]:
                self.boatClic = (3,"contre-torpilleur")
            else:
                print("This ship is already on the map")
        elif key =="porte-avions":
            if self.porte_avions==[]:
                self.boatClic = (5,"porte-avions")
            else:
                print("This ship is already on the map")
        elif key =="torpilleur":
            if self.torpilleur==[]:
                self.boatClic = (2,"torpilleur")
            else:
                print("This ship is already on the map")
        elif key =="croiseur":
            if self.croiseur==[]:
              self.boatClic = (4,"croiseur")
            else:
                print("This ship is already on the map")
        
    def BoatDict(self, position):
        ''' Insère les positions des navires en mémoire '''
        self.squarePosition=position
        self.IsThereABoat(self.squarePosition)
        if self.boatClic==(3,"sous-marin"):
            if self.orientation==True:
                if self.testv>=-302 and self.is_a_boat==False:
                    for i in range (self.boatClic[0]):
                            self.sous_marin.append((position[0],position[1]+i))
                            self.all_position.append((position[0],position[1]+i))
            else:
                if self.testh <= 152 and self.is_a_boat==False:
                    for i in range (self.boatClic[0]):
                        self.sous_marin.append((position[0]+i,position[1]))
                        self.all_position.append((position[0]+i,position[1]))


        if self.boatClic==(2,"torpilleur"):
            if self.orientation==True:
                if self.testv>=-302 and self.is_a_boat==False:
                    for i in range (self.boatClic[0]):
                        self.torpilleur.append((position[0],position[1]+i))
                        self.all_position.append((position[0],position[1]+i))
            else:
                if self.testh <= 152 and self.is_a_boat==False:
                    for i in range (self.boatClic[0]):
                        self.torpilleur.append((position[0]+i,position[1])) 
                        self.all_position.append((position[0]+i,position[1]))
        
        if self.boatClic==(3,"contre-torpilleur"):
            if self.orientation==True:
                if self.testv>=-302 and self.is_a_boat==False:
                    for i in range (self.boatClic[0]):
                        self.contre_torpilleur.append((position[0],position[1]+i))
                        self.all_position.append((position[0],position[1]+i))
            else:
                if self.testh <= 152 and self.is_a_boat==False:
                    for i in range (self.boatClic[0]):
                        self.contre_torpilleur.append((position[0]+i,position[1])) 
                        self.all_position.append((position[0]+i,position[1]))
                        print(self.all_position) 


        if self.boatClic==(5,"porte-avions"):
            if self.orientation==True:
                if self.testv>=-302 and self.is_a_boat==False:
                    for i in range (self.boatClic[0]):
                        self.porte_avions.append((position[0],position[1]+i))
                        self.all_position.append((position[0],position[1]+i))
            else:
                if self.testh<=152 and self.is_a_boat==False:
                    for i in range (self.boatClic[0]):
                        self.porte_avions.append((position[0]+i,position[1]))
                        self.all_position.append((position[0]+i,position[1])) 
                       
        if self.boatClic==(4,"croiseur"):
            if self.orientation==True:
                if self.testv>=-302 and self.is_a_boat==False:
                    for i in range (self.boatClic[0]):
                        self.croiseur.append((position[0]--2,position[1]-2+i))
                        self.all_position.append((position[0]-2,position[1]-2+i))
            else:
                if self.testh<=152 and self.is_a_boat==False:    
                    for i in range (self.boatClic[0]):
                        self.croiseur.append((position[0]-2+i,position[1]-2))
                        self.all_position.append((position[0]-2+i,position[1]-2)) 


    def IsThereABoat(self, position):
        ''' Permet de vérifier si un navire est présent pour éviter que ceux-ci soit l'un par dessus l'autre. 
        Si un bateau se trouve sur l'une des cases prises par le navire que l'on cherche à placer, 
        la fonction retournera True, ce qui empêchera de placer le navire. '''
        if self.boatClic==(3,"sous-marin") or self.boatClic==(3,"contre-torpilleur"):
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
        
        if self.boatClic==(2,"torpilleur"):
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

        if self.boatClic==(4,"croiseur"):
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

        if self.boatClic==(3,"porte-avions"):
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

        if self.boatClic==(3,"porte-avions"):
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
    
    def Damage(self, attack):
        ''' Function that treats the attack results and sends them to the other player
        :param attack: a tuple (x,y) which are grid coordinates between 0 and 9'''
        if attack in self.torpilleur: #-------torpilleur
            self.torpilleur.remove(attack)
            self.all_position.remove(attack)
            if self.torpilleur == [] and self.all_position!=[]:
                self.client.rapporter('coulé')
            elif self.torpilleur ==[] and self.all_position==[]:
                self.client.rapporter('Win')
                self.ILost()
            else:
                self.client.rapporter('touché')
        elif attack in self.contre_torpilleur: #-------contre torpilleur
            self.contre_torpilleur.remove(attack)
            self.all_position.remove(attack)
            if self.contre_torpilleur == [] and self.all_position!=[]:
                self.client.rapporter('coulé')
            elif self.contre_torpilleur ==[] and self.all_position==[]:
                self.client.rapporter('Win')
                self.ILost()
            else:
                self.client.rapporter('touché')
        elif attack in self.croiseur: #-------croiseur
            self.croiseur.remove(attack)
            self.all_position.remove(attack)
            if self.croiseur == [] and self.all_position!=[]:
                self.client.rapporter('coulé')
            elif self.croiseur ==[] and self.all_position==[]:
                self.client.rapporter('Win')
                self.ILost()
            else:
                self.client.rapporter('touché')
        elif attack in self.porte_avions: #-------porte avions
            self.porte_avions.remove(attack)
            self.all_position.remove(attack)
            if self.porte_avions == [] and self.all_position!=[]:
                self.client.rapporter('coulé')
            elif self.porte_avions ==[] and self.all_position==[]:
                self.client.rapporter('Win')
                self.ILost()
            else:
                self.client.rapporter('touché')
        elif attack in self.sous_marin: #-------sous marin
            self.sous_marin.remove(attack)
            self.all_position.remove(attack)
            if self.sous_marin == [] and self.all_position!=[]:
                self.client.rapporter('coulé')
            elif self.sous_marin ==[] and self.all_position==[]:
                self.client.rapporter('Win')
                self.ILost()
            else:
                self.client.rapporter('touché')
        else:
            self.client.rapporter("A l'eau")
        print("self.sous_marin",self.sous_marin,"    self.porte_avions",self.porte_avions,"     self.croiseur", self.croiseur,"      self.contre_torpilleur", self.contre_torpilleur,"      self.torpilleur", self.torpilleur)
        print("self.all_position", self.all_position)

    def IWon(self):
        timee, delayy = time.time(), time.time()
        print("YOU WON THE GAME")
        self.Button('start',"image\\WIN.gif",0,0,150,150)
        while True:
            if (timee-delayy) > 5:
                self.display.bye()
            else:
                delayy=time.time()

    def ILost(self):
        timee, delayy = time.time(), time.time()
        print("YOU LOST THE GAME")
        self.Button("LOSE","image\\LOSE.gif",0,0,100,100)
        while True:
            if (timee-delayy) > 5:
                self.display.bye()
            else:
                delayy=time.time()


def Main():
    parser = argparse.ArgumentParser(prog="BattleShip : The Space Battle")
    parser.add_argument('playername', help='First Player', default="player one")
    parser.add_argument('othername', help='First Player', default=None)

    try:
        args = parser.parse_args()
        game = engineBattleShip(800,800, args.playername, args.othername)
    except:
        game = engineBattleShip(800,800)

    #Image de fond
    game.BgImage("image\\Background.gif")

    #Grids
    game.DrawGrid("Down Grid",10,10,400,200,350,0,0,0,102,102,255) #grille ou on place ses bateaux
    game.DrawGrid("Up Grid",10,10,250,275,75,0,0,0,102,102,255) #grille ou on attaque l'adversaire

    #Boutons
    game.Button('start',"image\\gifButtons\\start.gif",-330,330,150,150)
    game.Button("infos","image\\gifButtons\\Credits.gif",-350,-340,80,80)
    game.Button("exit","image\\gifButtons\\exit.gif",330,340,100,100)

    #Bateaux
    game.Button("torpilleur","image\\gifButtons\\boat2.gif",-350,50,67,25)
    game.Button("contre-torpilleur","image\\gifButtons\\boat3a.gif",-350,0,99,29)
    game.Button("sous-marin","image\\gifButtons\\boat3b.gif",-350,-50,105,29)
    game.Button("croiseur","image\\gifButtons\\boat4.gif",-325,-100,147,31)
    game.Button("porte-avions","image\\gifButtons\\boat5.gif",-322,-150,177,41)
    
    #Main loops
    print(game.contre_torpilleur, game.torpilleur, game.croiseur, game.porte_avions, "all position:", game.all_position)
    startTimeResponse = time.time()
    while game.GetWhileValue():
        #Initial window title
        game.WindowTitleNotification(3,"Welcome to BattleShip : The Space Battle","Please place your ships")
        game.ItemDetector(game.ClicManager())
        game.display.onkeypress(game.BoatVertical,'Right')
        game.display.onkeypress(game.BoatHorizontal,'Left')
        game.display.listen()
    print("You have now started the game")
    print("You are playing against : " + str(game.client.adversaire()))
    while True:
        #Actual gameplay
        #attaquer is in ItemDetector and the attack is sent when valid case is clicked
        tempClient=None
        while tempClient == None: #loop pour attendre l'attaque de l'adversaire
            game.ItemDetector(game.ClicManager(),game.client.attack_sent()) #ici on detecte lattaque du joueur
            timeNow3 = time.time()
            if (timeNow3 - startTimeResponse) >= 0.1:
                tempClient = game.client.attaquer()
                startTimeResponse =  time.time()
                if tempClient != None:
                    print(tempClient)
                    break
        tempClient2=(tempClient[0],tempClient[1])
        game.Damage(tempClient2) # on rapporte notre resultat de l'attaque a l'autre joueur
        rapporter = None
        while rapporter == None: # boucle qui attend le résultat de l'attaque de l'autre joueur
            timeNow3 = time.time()
            if (timeNow3-startTimeResponse) >= 0.1:
                rapporter = game.client.rapporter()
                startTimeResponse = time.time()
                if rapporter != None:
                    print(rapporter)
                    if rapporter == "Win":
                        game.IWon()
                    break
        game.IWon()
        

        ##text in window title
        #if game.client.attack_sent()==False:
        #    game.WindowTitleNotification(0.5,"-_-It's your turn-_-","_-_IT'S YOUR TURN_-_")
        #elif game.client.attack_sent()==True or game.client.report_sent()==True :
        #    game.WindowTitleNotification(1,"Please wait.","Please wait..","Please wait...")
        #game.ItemDetector(game.ClicManager())

if __name__ == "__main__":
    Main()