"""Description.

Résolution du problème de flot maximal pour un réseau d'adduction d'eau.
Utilise l'algorithme de Dinic via networkx.
"""

import networkx as nx
from .data import ReseauEau, SolutionFlot

SUPER_SOURCE = "S"
SUPER_PUITS = "T"
INFINI = 10_000


def construit_graphe(reseau: ReseauEau) -> nx.DiGraph:
    """Construit le graphe orienté pour le calcul du flot.

    Ajoute un super-source S relié aux réservoirs et un super-puits T
    relié aux villes, afin d'avoir un réseau à source et puits uniques.
    """
    graphe = nx.DiGraph()
    for noeud, capacite in reseau.reservoirs.items():
        graphe.add_edge(SUPER_SOURCE, noeud, capacity=capacite)
    for arc in reseau.arcs:
        graphe.add_edge(arc.origine, arc.destination, capacity=arc.capacite)
    for ville in reseau.villes:
        graphe.add_edge(ville, SUPER_PUITS, capacity=INFINI)
    return graphe


def resolution(reseau: ReseauEau) -> SolutionFlot:
    """Calcule le flot maximal pouvant transiter dans le réseau.

    Retourne un objet SolutionFlot contenant la valeur totale et la
    répartition du flot livré à chaque ville.
    """
    graphe = construit_graphe(reseau)
    valeur, flot = nx.maximum_flow(graphe, SUPER_SOURCE, SUPER_PUITS)
    repartition = {ville: flot[ville][SUPER_PUITS] for ville in reseau.villes}
    return SolutionFlot(
        reseau=reseau,
        valeur=int(valeur),
        repartition=repartition,
    )


def capacites_optimales(reseau: ReseauEau) -> tuple[int, int, int]:
    """Détermine les capacités minimales sur A→E et I→L pour atteindre le
    flot maximal théorique du réseau.

    Retourne:
        capacite_ae: nouvelle capacité pour l'arc A→E.
        capacite_il: nouvelle capacité pour l'arc I→L.
        flot_optimal: flot total atteint avec ces capacités.
    """
    reseau_illimite = reseau.avec_arc_modifie("A", "E", INFINI).avec_arc_modifie("I", "L", INFINI)
    flot_max = resolution(reseau_illimite).valeur

    for capacite_il in range(1, INFINI):
        for capacite_ae in range(1, INFINI):
            reseau_test = (
                reseau
                .avec_arc_modifie("A", "E", capacite_ae)
                .avec_arc_modifie("I", "L", capacite_il)
            )
            if resolution(reseau_test).valeur >= flot_max:
                return capacite_ae, capacite_il, flot_max
    return INFINI, INFINI, flot_max


def ordre_travaux(reseau: ReseauEau, capacite_ae: int, capacite_il: int) -> list[tuple[str, int]]:
    """Détermine l'ordre optimal de réfection des deux canalisations.

    Teste les deux ordres possibles et retourne celui qui maximise le flot
    après la première étape.

    Retourne:
        liste de (description_travaux, flot_après_travaux) dans l'ordre optimal.
    """
    flot_ae_premier = resolution(reseau.avec_arc_modifie("A", "E", capacite_ae)).valeur
    flot_il_premier = resolution(reseau.avec_arc_modifie("I", "L", capacite_il)).valeur
    flot_final = resolution(
        reseau.avec_arc_modifie("A", "E", capacite_ae).avec_arc_modifie("I", "L", capacite_il)
    ).valeur

    if flot_ae_premier >= flot_il_premier:
        return [
            (f"Réfection A→E (cap={capacite_ae})", flot_ae_premier),
            (f"Réfection I→L (cap={capacite_il})", flot_final),
        ]
    return [
        (f"Réfection I→L (cap={capacite_il})", flot_il_premier),
        (f"Réfection A→E (cap={capacite_ae})", flot_final),
    ]