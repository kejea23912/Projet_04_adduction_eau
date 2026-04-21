"""Description.

Tests unitaires du module data.
"""

import pytest
from pydantic import ValidationError
from adduction_eau.data import Arc, ReseauEau, SolutionFlot, RESEAU_ADDUCTION

def test_arc_capacite_nulle_invalide():
    with pytest.raises(ValidationError):
        Arc(origine="A", destination="B", capacite=0)

def test_arc_capacite_negative_invalide():
    with pytest.raises(ValidationError):
        Arc(origine="A", destination="B", capacite=-5)

def test_arc_str():
    assert str(Arc(origine="A", destination="E", capacite=7)) == "(A → E, cap=7)"

def test_reseau_valide():
    reseau = ReseauEau(
        reservoirs={"A": 15},
        arcs=[Arc(origine="A", destination="J", capacite=10)],
        villes=["J"],
    )
    assert reseau.reservoirs["A"] == 15

def test_reseau_ville_absente_des_arcs():
    with pytest.raises(ValidationError):
        ReseauEau(
            reservoirs={"A": 15},
            arcs=[Arc(origine="A", destination="J", capacite=10)],
            villes=["X"], 
        )

def test_reseau_adduction_est_valide():
    assert len(RESEAU_ADDUCTION.arcs) == 16
    assert set(RESEAU_ADDUCTION.villes) == {"J", "K", "L"}
    assert RESEAU_ADDUCTION.reservoirs["D"] == 10

def test_avec_arc_modifie_immutabilite():
    modifie = RESEAU_ADDUCTION.avec_arc_modifie("A", "E", 20)
    arc_ae = next(a for a in modifie.arcs if a.origine == "A" and a.destination == "E")
    arc_ae_orig = next(a for a in RESEAU_ADDUCTION.arcs if a.origine == "A" and a.destination == "E")
    assert arc_ae.capacite == 20
    assert arc_ae_orig.capacite == 7 

def test_avec_arc_modifie_ne_touche_pas_les_autres():
    modifie = RESEAU_ADDUCTION.avec_arc_modifie("A", "E", 20)
    arc_il = next(a for a in modifie.arcs if a.origine == "I" and a.destination == "L")
    assert arc_il.capacite == 4

def test_solution_flot_valide():
    sol = SolutionFlot(
        reseau=RESEAU_ADDUCTION,
        valeur=37,
        repartition={"J": 4, "K": 30, "L": 3},
    )
    assert sol.valeur == 37

def test_solution_flot_repartition_incoherente():
    with pytest.raises(ValidationError):
        SolutionFlot(
            reseau=RESEAU_ADDUCTION,
            valeur=37,
            repartition={"J": 4, "K": 30, "L": 10}, 
        )

def test_solution_flot_villes_manquantes():
    with pytest.raises(ValidationError):
        SolutionFlot(
            reseau=RESEAU_ADDUCTION,
            valeur=37,
            repartition={"J": 37}, 
        )