## PROBLEME DU VOYAGEUR DE COMMERCE
## Résolution par algorithme génétique
## Version 1.0

# Imports
from math import *
from random import *
from copy import *

# Functions
def create_and_fill_double_list(size_x, size_y):
	l = []
	for a in range(size_x):
		l.append([])
		for _ in range(size_y):
			l[a].append(0.0)

	return l

# Classes
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


villes = [Vect(0.0, 0.0), Vect(1.0, 0.0), Vect(1.0, 1.0), Vect(0.0, 1.0)]
	
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
			print(i,probaChemin2[i])
			nbRand = randrange(int(sum(probaChemin2[i])*100))
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


######   MAIN   ######

population = []
generation = 1

for i in range(100):
	population.append(Voyager(villes[0]))
	population[i].calcDistanceTotale()
	
algo = GeneticAlgorithm(0.2, 0.1)
algo.bindPopulation(population)


while (generation < 6):
	# On fait marcher l'algo
	algo.selectionIndividus()
	algo.croisementGenes()
	algo.mutationGenes()

	# On recalcule les distances parcourues totales par la nouvelle génération
	for i in range(100):
		population[i].calcDistanceTotale(algo.probaChemin)

	#On dit qu'on passe à la génération suivante
	generation += 1

	print(generation)
