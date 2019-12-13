## PROBLEME DU VOYAGEUR DE COMMERCE
## Résolution par algorithme génétique
## Version 3.0

# Imports
import turtle as t
from math import *
from random import *
from copy import *
import csv

#Variables globales beaucoup utilisées
nom_villes = []
villes = []

#Classes
class Affichage():
	def __init__(self):
		t.bgpic("france.png")
		t.hideturtle()

		#Deuxième Tortue pour l'affichage des stats
		self.turtleStats = t.Turtle()
		self.turtleStats.hideturtle()

		#pour l'affichage dans la France (dans self.dessineVilles)
		self.origine = Vect(-4.4546, 42)
		self.hImage = self.wImage = 500
		self.hReel = 9.2
		self.wReel = 12.8
		self.scaleFactorX = self.wImage/self.wReel
		self.scaleFactorY = self.hImage/self.hReel

	def dessineCroix(self, point, taille, gras=False):
		#On rend la tortue très rapide juste pour le dessin des croix
		t.speed(0)
		if(gras): #Pour la croix qui reprénsente la ville de départ et d'arrivée
			t.pensize(3)
			t.pencolor("blue")
		else: #Pour les autres
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
		#Et on ralentit au maximum la tortue pour la suite du programme
		t.speed(1)

	def dessinerChemin(self, chemin):
		#Vitesse régulée gràace au tracer
		t.tracer(1,0)
		t.pensize(3)
		t.pencolor("red")
		t.goto(villes[0].x, villes[0].y)
		t.pendown()
		for c in chemin:
			t.goto(villes[c].x, villes[c].y)
		t.goto(villes[0].x, villes[0].y)
		t.penup()

	def dessineVilles(self):
		for i in range(len(villes)):
			villes[i] = villes[i] - self.origine
			villes[i].x *= self.scaleFactorX
			villes[i].y *= self.scaleFactorY
			villes[i] = villes[i] - Vect(250,250)
			self.dessineCroix(villes[i], 10, (i==0))

	def gestionEffacements(self, effacer):
		#Tracer desactive les animations de dessin (déplacement instantané)
		t.tracer(100, 0)
		if (effacer == True):
			for _ in range(len(villes) + 2):
				t.undo()
		for _ in range(3):
			self.turtleStats.undo()

	def displayStats(self):
		self.turtleStats.penup()
		self.turtleStats.pencolor("black")
		self.turtleStats.goto(-aff.wImage/2, aff.hImage/2)
		self.turtleStats.write("Nombre de villes : " + str(len(villes)), False, "left", ("Arial", 10, "normal"))
		self.turtleStats.goto(-aff.wImage/2, aff.hImage/2 - 15)
		self.turtleStats.write("Generation : " + str(algo.generation), False, "left", ("Arial", 10, "normal"))
		self.turtleStats.goto(-aff.wImage/2, aff.hImage/2 - 30)
		self.turtleStats.write("Distance : " + "%.2f" % algo.meilleurDist, False, "left", ("Arial", 10, "normal"))

class GestionFichier():
	def __init__(self, nameFile):
		self.file = nameFile

	def getElem(self, i, j):
		with open(self.file, 'r') as f:
			reader = csv.reader(f)
			for line in reader:
				if reader.line_num - 1 == i:
					return line[j]

	def fill_villes(self):
		if self.file == "villes.txt":
			with open(self.file, "r") as f_villes:
				contenu = f_villes.read()

			w_contenu = contenu.split()
	
			for i in range(round(len(w_contenu) / 3)):
				nom_villes.append(w_contenu[3*i])
				villes.append(Vect(float(w_contenu[3*i + 1]), float(w_contenu[3*i + 2])))

		elif self.file == "villes.csv":
			with open(self.file, "r") as f_villes:
				contenu = csv.reader(f_villes)
				for row in contenu:
					nom_villes.append(row[0])
					villes.append(Vect(float(row[2]), float(row[1])))
		else:
			print("Erreur : Fichier de villes non existant.")

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

# Représente un voyageur
class Voyager():
	def __init__(self, posInit):
		self.posInit = posInit
		self.position = posInit
		self.distanceParcourue = 0
		self.chemin = []
		
	def __repr__(self): #pour le sorted de l'algorithm
		return repr(self.distanceParcourue)
		
	#On déplace le Voyager à un une ville et on incrémente sa distanceTotale
	def deplacerA(self, posVille):
		vectDeplacement = posVille - self.position
		self.distanceParcourue += vectDeplacement.module()
		self.position = posVille
		
	#On fait faire tout un chemin au Voyager
	def calcDistanceTotale(self, probaChemin=[]):
		self.reset()
		if(self.chemin == []): #Ici deplacement totalement aléatoire
			randList = list(range(1,len(villes)))
			shuffle(randList)
			for i in randList :
				self.deplacerA(villes[i])
				self.chemin.append(i)
		else:
			self.deplacement(probaChemin)
			self.deplacerA(self.posInit)
		
	#On déplace le Voyager selon la pondération imposée par probaChemin
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
		self.probaChemin = self.create_and_fill_double_list(len(villes), len(villes))
		self.population = []
		self.generation = 0
		self.nbIndividus = 100

		# On enregistre le meilleur le chemin de toute la simultaion
		# au cas où notre algorithme passe une fois par un bon chemin
		# mais il s'en détourne à cause d'un mauvais random
		self.meilleurDistALL = float("inf")
		self.meilleurCheminALL = []
		self.meilleurCheminStrALL = []
		
		#On crée et on lance la génération 0
		for i in range(self.nbIndividus):
			self.population.append(Voyager(villes[0]))
			self.population[i].calcDistanceTotale()

	## Bind un liste d'individus qui va être manipulée lors de l'évolution de l'algorithme
	#def bindPopulation(self, population):
	#	self.population = population
	#	self.nbIndividus = len(population)

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
		classement = 1
		divAverage = len(self.meilleursIndividus)
		for voyager in self.meilleursIndividus:
			if (classement == 1):
				poids = 3					# Valeur à tester pour changer le poids du premier
				divAverage += poids - 1
			elif (classement == 2):
				poids = 2					# Valeur à tester pour changer le poids du deuxième
				divAverage += poids - 1
			else:
				poids = 1
			self.probaChemin[0][voyager.chemin[0]] += poids
			for i in range(len(voyager.chemin) - 1):
				self.probaChemin[voyager.chemin[i]][voyager.chemin[i+1]] += poids
			classement += 1

		# A cet instant, on a un tableau qui contient des entiers représentatifs du nombre de passe d'une ville à un autre
		# On veut donc transformer celui-ci en tableau contenant les probabilités de passer d'une ville à une autre
		# pour la prochaine génération (nombre compris entre 0 et 1)
		# On divise donc chaque case du tableau "probaChemin" par le nombre d'individus sélectionnés
		for x in range(len(villes)):
			for y in range(1, len(villes)):
				self.probaChemin[x][y] = float(self.probaChemin[x][y] / divAverage)
	
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
		seuil = 1E-7
		for x in range(len(villes)):
			if (sum(self.probaChemin[x]) < seuil and sum(self.probaChemin[x]) != 0 or self.generation > 200):
				self.meilleurDist = self.meilleurDistALL
				return True
		return False

	def setMeilleur(self):
		self.meilleurVoyageur = self.getMeilleurActuel()
		self.meilleurDist = self.meilleurVoyageur.distanceParcourue
		self.meilleurChemin = self.meilleurVoyageur.chemin
		self.meilleurCheminStr = []
		self.meilleurCheminStr.append("Paris")
		for e in self.meilleurVoyageur.chemin:
			self.meilleurCheminStr.append(nom_villes[int(e)])
		self.meilleurCheminStr.append("Paris")

		if(self.meilleurDist < self.meilleurDistALL):
			self.meilleurDistALL = self.meilleurDist
			self.meilleurCheminALL = self.meilleurChemin
			self.meilleurCheminStrALL = self.meilleurCheminStr

	def create_and_fill_double_list(self, size_x, size_y):
		l = []
		for a in range(size_x):
			l.append([])
			for _ in range(size_y):
				l[a].append(0.0)
		return l


######   MAIN   ######

file = GestionFichier("villes.csv")
file.fill_villes()

aff = Affichage()
aff.dessineVilles()

pastChemin = []

#On crée notre algorithme et on lance la génération 0
algo = GeneticAlgorithm(0.18, 0.23) # Meilleurs taux découverts après de nombreux tests

# Tant que l'algo n'a pas trouvé la "solution" :
while (not(algo.foundSolution())):
	# On récupère le meilleur individu de la génération actuelle
	algo.setMeilleur()
	
	#Gestion effacements (avant les 2 fonctions de dessin)
	if(algo.generation != 0):
		aff.gestionEffacements(algo.meilleurChemin != pastChemin)

	#Affichage stats actuelles
	aff.displayStats()

	#Affichage meilleur chemin de la génération s'il est différent de celui d'avant
	if(algo.meilleurChemin != pastChemin):
		aff.dessinerChemin(algo.meilleurChemin)

	# On fait marcher l'algo
	algo.selectionIndividus()
	algo.croisementGenes()
	algo.mutationGenes()

	# On recalcule les distances parcourues totales par la nouvelle génération
	for i in range(100):
		algo.population[i].calcDistanceTotale(algo.probaChemin)

	#On dit qu'on passe à la génération suivante
	algo.generation += 1

	# On enregitre le meilleur chemin de la génération d'avant pour le comparer avec celui d'après
	pastChemin = deepcopy(algo.meilleurChemin)

aff.gestionEffacements(True)
aff.displayStats()

print("Meilleur résultat obtenu au bout de ", algo.generation, " generations :")
print(algo.meilleurCheminStrALL)
print("Distance totale parcourue : ", algo.meilleurDistALL)

aff.dessinerChemin(algo.meilleurCheminALL)

t.done()