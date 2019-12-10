## PROBLEME DU VOYAGEUR DE COMMERCE
## Résolution par algorithme génétique
## Version 1.0

# Imports
from math import *
from random import *

class GeneticAlgorithm():
    # Constructeur
    # Paramètres :
    # - Taux de sélection : quel pourcentage de la population va être retenu comme "meilleurs candidats"
    # - Taux de mutation  : quelle est la chance de mutation d'un gène lors de l'étape de mutation de l'algorithme
    def __init__(self, tauxSelection, tauxMutation):
        self.tauxSelection = tauxSelection
        self.tauxMutation = tauxMutation

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
        self.probaChemin = []
        for voyager in self.meilleursIndividus:
            self.probaChemin[0][voyager.chemin[0]] += 1
            for i in range(len(villes) - 1):
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
            diff = averages[x] - self.probaChemin[x][y]
            for y in range(1, len(villes)):
                self.probaChemin[x][y] += (diff * self.tauxMutation)
