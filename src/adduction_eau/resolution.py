"""Description.

Résolution du problème de flot maximal pour un réseau d'adduction d'eau.
Utilise l'algorithme de Dinic via networkx.
"""

import networkx as nx
from .data import ReseauEau, SolutionFlot
from pydantic import BaseModel

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



#  Partie supplémentaire des consignes

class PropositionAmelioration(BaseModel):
    """Proposition d'amélioration d'un arc pour augmenter le flot du réseau."""

    origine: str
    destination: str
    capacite_actuelle: int
    capacite_requise: int

    @property
    def gain(self) -> int:
        """Augmentation de capacité nécessaire."""
        return self.capacite_requise - self.capacite_actuelle

    def __str__(self) -> str:
        return (
            f"({self.origine}→{self.destination} : "
            f"{self.capacite_actuelle} → {self.capacite_requise}, +{self.gain})"
        )

class SolutionAmelioration(BaseModel):
    """Solution d'optimisation : arcs à améliorer pour atteindre le flot maximal théorique."""

    flot_actuel: int
    flot_theorique: int
    propositions: list[PropositionAmelioration]

    @property
    def gain_flot(self) -> int:
        """Gain de flot total apporté par les améliorations."""
        return self.flot_theorique - self.flot_actuel


def arcs_a_ameliorer(reseau: ReseauEau) -> SolutionAmelioration:
    """Trouve le minimum d'arcs à améliorer pour atteindre le flot maximal théorique.

    Le flot maximal théorique est celui obtenu en supprimant toutes les contraintes
    de capacité sur les canalisations (arcs), les capacités des réservoirs restant fixes.

    Algorithme en deux phases :

    Phase 1 — Sélection gloutonne des arcs à améliorer :
        À chaque itération, identifie la coupe minimale du réseau courant et choisit
        l'arc de la coupe dont l'amélioration à capacité illimitée maximise le gain
        de flot. L'arc sélectionné est temporairement mis à INFINI, puis on répète
        jusqu'à atteindre le flot théorique.

    Phase 2 — Dichotomie séquentielle pour les capacités minimales :
        Pour chaque arc identifié en phase 1 (dans l'ordre de sélection), cherche
        par dichotomie la capacité minimale permettant d'atteindre le flot théorique,
        en supposant que les arcs précédemment traités sont à leur capacité calculée
        et que les arcs suivants sont encore à capacité illimitée.

    Seuls les arcs dont la capacité requise est strictement supérieure à la capacité
    actuelle sont inclus dans les propositions.
    """
    arcs_originaux = {(a.origine, a.destination): a.capacite for a in reseau.arcs}
    reseau_illimite = reseau
    for arc in reseau.arcs:
        reseau_illimite = reseau_illimite.avec_arc_modifie(arc.origine, arc.destination, INFINI)

    flot_theorique = resolution(reseau_illimite).valeur
    flot_actuel = resolution(reseau).valeur

    if flot_actuel >= flot_theorique:
        return SolutionAmelioration(
            flot_actuel=flot_actuel,
            flot_theorique=flot_theorique,
            propositions=[],
        )

    reseau_courant = reseau
    arcs_selectionnes: list[tuple[str, str]] = []
    deja_selectionnes: set[tuple[str, str]] = set()

    while resolution(reseau_courant).valeur < flot_theorique:
        graphe = construit_graphe(reseau_courant)
        _, (S, T) = nx.minimum_cut(graphe, SUPER_SOURCE, SUPER_PUITS)

        candidats = [
            (u, v) for u, v in graphe.edges()
            if u in S and v in T
            and (u, v) in arcs_originaux
            and (u, v) not in deja_selectionnes
        ]
        if not candidats:
            break  

        meilleur = max(
            candidats,
            key=lambda arc: resolution(
                reseau_courant.avec_arc_modifie(*arc, INFINI)
            ).valeur,
        )
        reseau_courant = reseau_courant.avec_arc_modifie(*meilleur, INFINI)
        arcs_selectionnes.append(meilleur)
        deja_selectionnes.add(meilleur)

    
    propositions: list[PropositionAmelioration] = []
    caps_fixes: list[tuple[tuple[str, str], int]] = []

    for i, arc in enumerate(arcs_selectionnes):
        reseau_contexte = reseau
        for arc_fixe, cap_fixe in caps_fixes:
            reseau_contexte = reseau_contexte.avec_arc_modifie(*arc_fixe, cap_fixe)
        for arc_suivant in arcs_selectionnes[i + 1:]:
            reseau_contexte = reseau_contexte.avec_arc_modifie(*arc_suivant, INFINI)

        lo, hi = 1, INFINI
        while lo < hi:
            mid = (lo + hi) // 2
            if resolution(reseau_contexte.avec_arc_modifie(*arc, mid)).valeur >= flot_theorique:
                hi = mid
            else:
                lo = mid + 1
        cap_requise = lo
        cap_actuelle = arcs_originaux[arc]
        caps_fixes.append((arc, max(cap_actuelle, cap_requise)))

        if cap_requise > cap_actuelle:
            propositions.append(
                PropositionAmelioration(
                    origine=arc[0],
                    destination=arc[1],
                    capacite_actuelle=cap_actuelle,
                    capacite_requise=cap_requise,
                )
            )

    return SolutionAmelioration(
        flot_actuel=flot_actuel,
        flot_theorique=flot_theorique,
        propositions=propositions,
    )