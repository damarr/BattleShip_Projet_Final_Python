import turtle, os

class Battleship():
    def __init__(self,pseudo,width,height):
        """methode pour l'initialisation du jeu """
        #parametrage de la fen�tre
        self.fen = turtle.Screen()
        self.fen.setup(width,height,startx=None,starty=None)
        self.width=width; self.height=height
        self.fen.title("Battleship")
        #parametrage de la tortue
        self.turt = turtle.Turtle()
        #self.turt.ht() #on cache la tortue
        Battleship.environnementCreer(self)
        self.tour="joueur" #creer une fonction pour savoir si cest notre tour
        self.fen.onclick(Battleship.metunx) #fonction appel�e quand on clicke
        self.fen.mainloop()

    def environnementCreer(self):
        self.turt._tracer(2)
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
        if x<-350 or x>300 or y<-50 or y>300:
            return "Erreur"
        if self.tour=="joueur":
            startx=-350; starty=-50
        else:
            startx=0; starty=-50
        """ boucles pour determiner la colonne et la rangee qu'on a clique : retourne le tuple"""
        indicex=0; indicey=10
        while x>startx and startx<(startx+300):
            startx+=30
            indicex+=1
        while y>starty and starty<250:
            starty+=30
            indicey-=1
        return (indicex-1,indicey-1)

    def metunx(self,coord):
        self.fen.onclick(None,btn=1)
        indices=Battleship.coordonnee(self,coord[0],coord[1])
        print(self.grillejoueur[indices])
        self.turt.goto(self.grillejoueur[indices][0],self.grillejoueur[indices][1])
        self.turt.color("blue")
        self.turt.write("X", move=True, align="center", font=("Arial", 9, "normal"))
        self.fen.onclick(metunx, btn=1)



jeubattleship = Battleship("Nadia",900,600)
print(jeubattleship.coordonnee(-320,100))
jeubattleship.metunx((-320,100))