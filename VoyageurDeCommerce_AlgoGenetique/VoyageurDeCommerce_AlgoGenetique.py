## PROBLEME DU VOYAGEUR DE COMMERCE
## Résolution par algorithme génétique
## Version 3.0

# Imports
import turtle as t
from math import *
from random import *
from copy import *
import csv

# Functions
def create_and_fill_double_list(size_x, size_y):
	l = []
	for a in range(size_x):
		l.append([])
		for _ in range(size_y):
			l[a].append(0.0)

	return l

def getElem(file, i, j):
    with open(file, 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            if reader.line_num - 1 == i:
                return line[j]

def dessineCroix(point, taille, gras=False):
	if(gras):
		t.pensize(3)
		t.pencolor("blue")
	else:
		t.pensize(2)
		t.pencolor("black")
	t.penup()
	t.goto(point.x + taille, point.y + taille)
	t.pendown()
	t.goto(point.x - taille, point.y - taille)
	t.penup()
	t.goto(point.x - taille, point.y + taille)
	t.pendown()
	t.goto(point.x + taille, point.y - taille)
	t.penup()

def dessinerChemin(chemin):
	t.pensize(3)
	t.pencolor("red")
	t.goto(villes[0].x, villes[0].y)
	t.pendown()
	t.speed(2)
	for c in chemin:
		t.goto(villes[c].x, villes[c].y)
		print(villes[c].str())
	t.goto(villes[0].x, villes[0].y)
	t.penup()
	
t.bgpic("france.png")
t.speed(0)
t.hideturtle()

# Classes
# Rend la manipulation de vecteurs plus facile.
class Vect():
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def module(self):
		return sqrt(self.x**2 + self.y**2)

	def __sub__(self, otherVect):
		return Vect(self.x-otherVect.x, self.y-otherVect.y)

	def str(self):
		return "x : " + str(self.x) + ", y : " + str(self.y)

# Lecture du fichier contenant les coordonnées GPS
# Stockage des noms des villes dans la list "nom_villes"
# Stockage des coordonnées sous la forme de vecteurs dans la list "villes"

file = "villes.txt"
nom_villes = []
villes = []

if file == "villes.txt":
	with open(file, "r") as f_villes:
		contenu = f_villes.read()

	w_contenu = contenu.split()
	
	for i in range(round(len(w_contenu) / 3)):
		nom_villes.append(w_contenu[3*i])
		villes.append(Vect(float(w_contenu[3*i + 1]), float(w_contenu[3*i + 2])))

elif file == "villes.csv":
	with open(file, "r") as f_villes:
		contenu = csv.reader(f_villes)
		for row in contenu:
			nom_villes.append(row[0])
			villes.append(Vect(float(row[2]), float(row[1])))

else:
	print("Erreur : Fichier de villes non existant.")

origine = Vect(-4.4546, 42)
hImage = wImage = 500
hReel = 9.2
wReel = 12.8
scaleFactorX = wImage/wReel
scaleFactorY = hImage/hReel

for i in range(len(villes)):
	villes[i] = villes[i] - origine
	villes[i].x *= scaleFactorX
	villes[i].y *= scaleFactorY
	villes[i] = villes[i] - Vect(250,250)
	dessineCroix(villes[i], 10, (i==0))

# Représente un voyageur
class Voyager():
	def __init__(self, posInit):
		self.posInit = posInit
		self.position = posInit
		self.distanceParcourue = 0
		self.chemin = []
		
	def __repr__(self): #pour le sorted de l'algorithm
		return repr(self.distanceParcourue)
		
	def deplacerA(self, posVille):
		vectDeplacement = posVille - self.position
		self.distanceParcourue += vectDeplacement.module()
		self.position = posVille
		
	def calcDistanceTotale(self, probaChemin=[]):
		self.reset()
		if(self.chemin == []):
			randList = list(range(1,len(villes)))
			shuffle(randList)
			for i in randList :
				self.deplacerA(villes[i])
				self.chemin.append(i)
		else:
			self.deplacement(probaChemin)
			self.deplacerA(self.posInit)
		
	def deplacement(self, probaChemin):
		self.chemin.clear()
		probaChemin2 = deepcopy(probaChemin)
		i=0
		while(len(self.chemin) != len(villes) - 1):
			sumProba = 0
			try:
				nbRand = randrange(ceil(sum(probaChemin2[i])*100))
			except:
				nbRand = 150
			for j in range(1,len(villes)):
				sumProba += probaChemin2[i][j]
				if(not(j in self.chemin) and (nbRand < sumProba*100)):
					self.deplacerA(villes[j])
					self.chemin.append(j)
					i=j
					for k in range(len(villes)):
						probaChemin2[k][j] = 0
					break
				
	def reset(self):
		self.position = self.posInit
		self.distanceParcourue = 0

# Permet de créer et executer un algorithme génétique sur une population donnée
class GeneticAlgorithm():
	# Constructeur
	# Paramètres :
	# - Taux de sélection : quel pourcentage de la population va être retenu comme "meilleurs candidats"
	# - Taux de mutation  : quelle est la chance de mutation d'un gène lors de l'étape de mutation de l'algorithme

	def __init__(self, tauxSelection, tauxMutation):
		self.tauxSelection = tauxSelection
		self.tauxMutation = tauxMutation
		self.probaChemin = create_and_fill_double_list(len(villes), len(villes))

	# Bind un liste d'individus qui va être manipulée lors de l'évolution de l'algorithme
	def bindPopulation(self, population):
		self.population = population
		self.nbIndividus = len(population)

	def getMeilleurActuel(self):
		self.population.sort(key=lambda voyager: voyager.distanceParcourue)
		return deepcopy(self.population[0])
		
	# Algorithme de sélection des meilleurs individus
	def selectionIndividus(self):
		nbIndividusSelect = int(self.nbIndividus * self.tauxSelection)
		self.population.sort(key=lambda voyager: voyager.distanceParcourue)
		self.meilleursIndividus = self.population[:nbIndividusSelect]

	# Algorithme de mélange des gènes
	def croisementGenes(self):
		for voyager in self.meilleursIndividus:
			self.probaChemin[0][voyager.chemin[0]] += 1
			for i in range(len(voyager.chemin) - 1):
				self.probaChemin[voyager.chemin[i]][voyager.chemin[i+1]] += 1

		# A cet instant, on a un tableau qui contient des entiers représentatifs du nombre de passe d'une ville à un autre
		# On veut donc transformer celui-ci en tableau contenant les probabilités de passer d'une ville à une autre
		# pour la prochaine génération (nombre compris entre 0 et 1)
		# On divise donc chaque case du tableau "probaChemin" par le nombre d'individus sélectionnés
		for x in range(len(villes)):
			for y in range(1, len(villes)):
				self.probaChemin[x][y] = float(self.probaChemin[x][y] / len(self.meilleursIndividus))
	
	# Algorithme de mutation des probabilités
	# Cette mutation des gènes permet à l'algorithme génétique de ne pas rester coincé dans une solution qui ne serait pas
	# la meilleure en réduisant le poids d'un chemin qui serait trop important et en augmentant celui d'un qui ne le serait
	# pas assez.
	def mutationGenes(self):
		averages = []
		for x in range(len(villes)):
			averages.append(sum(self.probaChemin[x]) / (len(villes) - 1))
			for y in range(1, len(villes)):
				diff = averages[x] - self.probaChemin[x][y]
				self.probaChemin[x][y] += (diff * self.tauxMutation)

	def foundSolution(self):
		seuil = 1E-10
		for x in range(len(villes)):
			if (sum(self.probaChemin[x]) < seuil and sum(self.probaChemin[x]) != 0):
				return True
		return False

######   MAIN   ######

population = []
generation = 1

for i in range(100):
	population.append(Voyager(villes[0]))
	population[i].calcDistanceTotale()

# Meilleurs valeurs de taux pour l'instant : (0.22, 0.21)	
algo = GeneticAlgorithm(0.22, 0.21)
algo.bindPopulation(population)

# Tant que l'algo n'a pas trouvé la "solution" :
while (not(algo.foundSolution())):
	# On récupère le meilleur individu de la génération actuelle
	meilleurVoyageur = algo.getMeilleurActuel()
	meilleurDist = meilleurVoyageur.distanceParcourue
	meilleurChemin = meilleurVoyageur.chemin
	meilleurCheminStr = []
	meilleurCheminStr.append("Paris")
	for e in meilleurVoyageur.chemin:
		meilleurCheminStr.append(nom_villes[int(e)])
	meilleurCheminStr.append("Paris")

	# On fait marcher l'algo
	algo.selectionIndividus()
	algo.croisementGenes()
	algo.mutationGenes()

	#print("Generation : ", generation)
	#print("Proba :")
	#for i in range(len(villes)):
	#	print(algo.probaChemin[i])
	#print("")

	# On recalcule les distances parcourues totales par la nouvelle génération
	for i in range(100):
		population[i].calcDistanceTotale(algo.probaChemin)

	#On dit qu'on passe à la génération suivante
	generation += 1

print("Resultat obtenu au bout de ", generation-1, " generations :")
print(meilleurCheminStr)
print("Distance totale parcourue : ", meilleurDist)

dessinerChemin(meilleurChemin)

print(meilleurChemin)

t.done()