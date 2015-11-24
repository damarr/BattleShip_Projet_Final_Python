import turtle, os

class Battleship():
    def __init__(self,pseudo,width,height):
        """methode pour l'initialisation du jeu """
        #parametrage de la fenetre
        self.fen = turtle.Screen()
        self.fen.setup(width,height,startx=None,starty=None)
        self.width=width; self.height=height
        #parametrage de la tortue
        self.turt = turtle.Turtle()
        #self.turt.ht() #on cache la tortue
        self.environnementCreer()
        self.fen.listen() #methode listen qui redirige tous les evenements (souris/clavier) vers la fenetre turtle
        self.tour="joueur" #creer une fonction pour savoir si cest notre tour
        self.fen.onclick(self.onClick,btn=1) #fonction appelee quand on clicke
        self.fen.onkeypress(self.onType, "space") #fonction appelee quand on pese sur space

    def environnementCreer(self):
        """ Creee lenvironnement de jeu et les grilles
        """
        self.fen.title("Battleship")
        self.turt._tracer(2) #desactive les animations
        self.fen.bgpic("background2.gif")
        self.turt.pen(fillcolor="black",pencolor="black",pensize=2,outline=1)
        
        #creer les deux grilles
        for i in [-350,0]:
            self.turt.penup()
            self.turt.goto(i,250)
            self.turt.pendown()
            for _ in range(11): #rangees
                self.turt.penup()
                self.turt.goto(i,250-(30*_))
                self.turt.pendown()
                self.turt.fd(30*10) # le c d'un carre est 30 pixels
            self.turt.penup()
            self.turt.right(90)
            self.turt.goto(i,250)   
            self.turt.pendown() 
            for _ in range(11): #colonnes
                self.turt.penup()
                self.turt.goto(i+(30*_),250)
                self.turt.pendown()
                self.turt.fd(30*10)
            self.turt.left(90)

        #creer un dictionnaire associant les indices de rang�es et colonnes aux coordonn�es du jeu
        self.grillejoueur={}; self.grilleadverse={}
        
        #grille joueur
        coordx=-350+30/2
        for x in range(10):
            coordy=250-30/2
            for y in range(10):
                self.grillejoueur[(x,y)]=(coordx,coordy)
                coordy-=30
            coordx+=30

        #grille adverse
        coordx=0
        for x in range(10):
            coordy=250
            for y in range(10):
                self.grilleadverse[(x,y)]=(coordx,coordy)
                coordy-=30
            coordx+=30
    
    def coordonnee(self,x,y):
        """ Fonction pour determiner la colonne et la rangee qu'on a clique : retourne le tuple
        Depend du tour du joueur ou de l'adversaire -- il faudra une fonction pour jouer a tour de role"""
        if self.tour=="joueur":
            if x<-350 or x>-30 or y>250 or y<-50:
                raise ValueError("Erreur de zone")
            startx=-350; starty=250 #on commence a gauche en haut
        else: #si self.tour=="adversaire"
            if x<0 or x>300 or y>250 or y<-50:
                raise ValueError("Erreur de zone")
            startx=0; starty=250 #on commence a gauche en haut
        indicex=0; indicey=0; limite=startx+300
        while x>startx and startx<=limite:
            startx+=30
            indicex+=1
        while y<starty and starty<=250:
            starty-=30
            indicey+=1
        return (indicex-1,indicey-1)

    def onClick(self,x,y):
        """ Lorsqu'on clique, on detecte la zone cliquee d'abord et ensuite les actions qui sont a prendre"""
        self.fen.onclick(None,btn=1)
        if (x>-350 and x<-30 and y<250 and y>-50) or (x>0 and x<300 and y<250 and y>-50):
            indices=self.coordonnee(x,y) #va chercher le numero de case a partir de ou on a clique
            self.turt.goto(self.grillejoueur[indices][0],self.grillejoueur[indices][1]) #va chercher le point central de la case ou on a clique
        else:
            #placer ici d'autres actions au click
            print("veuillez jouer svp")
        self.fen.onclick(self.onClick, btn=1)

    def onType(self):
        self.fen.onkeypress(None,"space")
        print("vous avez pese sur space")
        self.fen.onkeypress(self.onType,"space")


jeubattleship = Battleship("Nadia",900,600)
turtle.mainloop()