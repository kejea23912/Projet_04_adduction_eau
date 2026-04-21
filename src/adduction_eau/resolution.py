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
    graphe = nx.DiGraph()
    for noeud, capacite in reseau.reservoirs.items():
        graphe.add_edge(SUPER_SOURCE, noeud, capacity=capacite)
    for arc in reseau.arcs:
        graphe.add_edge(arc.origine, arc.destination, capacity=arc.capacite)
    for ville in reseau.villes:
        graphe.add_edge(ville, SUPER_PUITS, capacity=INFINI)
    return graphe


def resolution(reseau: ReseauEau) -> SolutionFlot:
    graphe = construit_graphe(reseau)
    valeur, flot = nx.maximum_flow(graphe, SUPER_SOURCE, SUPER_PUITS)
    repartition = {ville: flot[ville][SUPER_PUITS] for ville in reseau.villes}
    return SolutionFlot(
        reseau=reseau,
        valeur=int(valeur),
        repartition=repartition,
    )


def capacites_optimales(reseau: ReseauEau) -> tuple[int, int, int]:
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