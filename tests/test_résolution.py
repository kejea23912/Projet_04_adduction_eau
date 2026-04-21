"""Description.

Tests unitaires du module resolution.
"""

from adduction_eau.data import RESEAU_ADDUCTION, SolutionFlot
from adduction_eau.resolution import (
    construit_graphe,
    resolution,
    capacites_optimales,
    ordre_travaux,
    SUPER_SOURCE,
    SUPER_PUITS,
)


def test_graphe_contient_super_source_et_puits():
    graphe = construit_graphe(RESEAU_ADDUCTION)
    assert SUPER_SOURCE in graphe.nodes
    assert SUPER_PUITS in graphe.nodes


def test_graphe_arcs_reservoirs():
    graphe = construit_graphe(RESEAU_ADDUCTION)
    for reservoir, capacite in RESEAU_ADDUCTION.reservoirs.items():
        assert graphe[SUPER_SOURCE][reservoir]["capacity"] == capacite


def test_graphe_arcs_vers_puits():
    graphe = construit_graphe(RESEAU_ADDUCTION)
    for ville in RESEAU_ADDUCTION.villes:
        assert graphe.has_edge(ville, SUPER_PUITS)


def test_resolution_retourne_solution_flot():
    sol = resolution(RESEAU_ADDUCTION)
    assert isinstance(sol, SolutionFlot)


def test_resolution_flot_actuel():
    sol = resolution(RESEAU_ADDUCTION)
    assert sol.valeur == 37


def test_resolution_repartition_somme_egale_valeur():
    sol = resolution(RESEAU_ADDUCTION)
    assert sum(sol.repartition.values()) == sol.valeur


def test_resolution_augmenter_ae_ameliore_flot():
    sol_orig = resolution(RESEAU_ADDUCTION)
    sol_amelio = resolution(RESEAU_ADDUCTION.avec_arc_modifie("A", "E", 20))
    assert sol_amelio.valeur >= sol_orig.valeur


def test_capacites_optimales_atteignent_flot_max():
    cap_ae, cap_il, flot_optimal = capacites_optimales(RESEAU_ADDUCTION)
    assert cap_ae == 19
    assert cap_il == 15
    assert flot_optimal == 49


def test_capacites_optimales_coherentes():
    cap_ae, cap_il, flot_optimal = capacites_optimales(RESEAU_ADDUCTION)
    reseau_renove = (
        RESEAU_ADDUCTION
        .avec_arc_modifie("A", "E", cap_ae)
        .avec_arc_modifie("I", "L", cap_il)
    )
    assert resolution(reseau_renove).valeur == flot_optimal


def test_ordre_travaux_retourne_deux_etapes():
    etapes = ordre_travaux(RESEAU_ADDUCTION, 19, 15)
    assert len(etapes) == 2


def test_ordre_travaux_ae_en_premier():
    etapes = ordre_travaux(RESEAU_ADDUCTION, 19, 15)
    assert "A→E" in etapes[0][0]  # AE doit être fait en premier


def test_ordre_travaux_flot_croissant():
    etapes = ordre_travaux(RESEAU_ADDUCTION, 19, 15)
    assert etapes[1][1] >= etapes[0][1]
