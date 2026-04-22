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


def _recherche_binaire_min(reseau: ReseauEau, arc: tuple[str, str], capacite_fixe_arc: tuple[str, str], capacite_fixe: int, flot_cible: int) -> int:
    """Trouve par dichotomie la capacité minimale de `arc` pour atteindre `flot_cible`.

    Les autres arcs sont fixes. La capacité de `capacite_fixe_arc` est fixée à `capacite_fixe`.
    """
    borne_inf, borne_sup = 1, INFINI
    while borne_inf < borne_sup:
        milieu = (borne_inf + borne_sup) // 2
        reseau_test = (
            reseau
            .avec_arc_modifie(*arc, milieu)
            .avec_arc_modifie(*capacite_fixe_arc, capacite_fixe)
        )
        if resolution(reseau_test).valeur >= flot_cible:
            borne_sup = milieu
        else:
            borne_inf = milieu + 1
    return borne_inf


def capacites_optimales(reseau: ReseauEau) -> tuple[int, int, int]:
    """Détermine les capacités minimales pour A→E et I→L permettant d'atteindre le flot maximal.

    Utilise deux recherches binaires successives :
    1. Trouve la capacité minimale de A→E (avec I→L illimité).
    2. Trouve la capacité minimale de I→L (avec la capacité A→E trouvée en étape 1).

    Complexité : O(log(INFINI)) appels à `resolution` au lieu de O(INFINI²).
    """
    reseau_illimite = reseau.avec_arc_modifie("A", "E", INFINI).avec_arc_modifie("I", "L", INFINI)
    flot_max = resolution(reseau_illimite).valeur

    capacite_ae = _recherche_binaire_min(
        reseau,
        arc=("A", "E"),
        capacite_fixe_arc=("I", "L"),
        capacite_fixe=INFINI,
        flot_cible=flot_max,
    )
    capacite_il = _recherche_binaire_min(
        reseau,
        arc=("I", "L"),
        capacite_fixe_arc=("A", "E"),
        capacite_fixe=capacite_ae,
        flot_cible=flot_max,
    )
    return capacite_ae, capacite_il, flot_max


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