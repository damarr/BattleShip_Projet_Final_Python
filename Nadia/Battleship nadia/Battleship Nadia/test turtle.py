#test codes pour Turtle (classe de Tkinter)
import turtle

fenetre = turtle.Screen()
turt = turtle.Turtle() #Derived from RawTurtle is the subclass Turtle (alias: Pen), which draws on �the� Screen instance which is automatically created, if not already present.

#mettre des indices aux lignes et colonnes
#def ligne(width):
#    lignes=[]
#    for _ in range(9):

#la fenetre du jeu
fenetre.title("Battleship")
fenetre.bgcolor("#800080")
fenetre.setup(1000,800)        #turtle.screensize(canvwidth=None, canvheight=None, bg=None)

#la tortue
turt.pen(fillcolor="black",pencolor="#33cc8c",pensize=10,outline=1) #pour fillcolor : If turtleshape is a polygon, the interior of that polygon is drawn with the newly set fillcolor.
turt.speed(0) #trouver un meilleur code qui fait apparaitre le dessin directement
turt.penup()
turt.goto(-450,350)
turt.pendown()
#turt.write("texte", move=False, align="left", font=("Arial", 8, "normal"))
turt.ht() #je ne veux plus voir la tortue (ht ou hideturtle)
def grille():
    for _ in range(10):
        turt.begin_fill()
        for _ in range(4):
            turt.fd(50); turt.right(90)
        turt.end_fill()
        turt.fd(50)
grille()

def unCarre(x,y):
    fenetre.onclick(None,btn=1)
    print(x,y)
    turt.penup()
    turt.goto(x,y)
    turt.pendown()
    turt.fd(10)
    fenetre.onclick(unCarre, btn=1)

fenetre.onclick(unCarre) #fonction appel�e quand on clicke

fenetre.listen()
fenetre.mainloop()





class App:
    def __init__(self, largeur, hauteur):
        self.fen = turtle.Screen()
        self.fen.setup(largeur, hauteur)
        self.fen.onclick(self.tracerClic, btn=1)
        self.fen.onkeypress(self.changerModeEcriture, 'space')
        self.fen.listen()
        self.alex = turtle.Turtle()
    def tracerClic(self, x, y):
        self.fen.onclick(None, btn=1)
        self.alex.setheading(self.alex.towards(x, y))
        self.alex.goto(x, y)
        self.fen.onclick(self.tracerClic, btn=1)
    def changerModeEcriture(self):
        self.fen.onkeypress(None, 'space')
        if self.alex.isdown():
            self.alex.penup()
            self.alex.fillcolor('white')
        else:
            self.alex.pendown()
            self.alex.fillcolor('black')
        self.fen.onkeypress(self.changerModeEcriture, 'space')

x = App(800, 600)
turtle.mainloop()