"""Description.

Module implémentant les objets représentant le réseau d'adduction d'eau et sa solution.
"""

from typing import Self
from pydantic import BaseModel, NonNegativeInt, PositiveInt, model_validator
import json
from pathlib import Path

class Arc(BaseModel):
    """
    Représente une canalisation orientée entre deux nœuds avec une capacité maximale.
    Exemples:

    >>> Arc(origine="A", destination="E", capacite=7)   
    >>> Arc(origine="A", destination="E", capacite=0)
        Traceback (most recent call last):

    """

    origine: str
    destination: str
    capacite: PositiveInt

    def __str__(self) -> str:
        return f"({self.origine} → {self.destination}, cap={self.capacite})"


class ReseauEau(BaseModel):
    """Représente un réseau d'adduction d'eau.

    Attributs:
        reservoirs: dictionnaire nœud → capacité journalière disponible (milliers de m³).
        arcs: liste des canalisations avec leurs capacités.
        villes: nœuds de destination (puits du réseau).
    """

    reservoirs: dict[str, PositiveInt]
    arcs: list[Arc]
    villes: list[str]
    capacites_villes: dict[str, PositiveInt] | None = None

    @model_validator(mode="after")
    def verifie_coherence(self) -> Self:
        noeuds_arcs = {a.origine for a in self.arcs} | {a.destination for a in self.arcs}
        for ville in self.villes:
            if ville not in noeuds_arcs:
                raise ValueError(f"La ville '{ville}' n'apparaît dans aucun arc.")
        return self

    def avec_arc_modifie(self, origine: str, destination: str, nouvelle_capacite: PositiveInt) -> "ReseauEau":
        """Retourne un nouveau réseau avec la capacité d'un arc modifiée."""
        nouveaux_arcs = [
            Arc(origine=a.origine, destination=a.destination, capacite=nouvelle_capacite)
            if (a.origine == origine and a.destination == destination)
            else a
            for a in self.arcs
        ]
        return self.model_copy(update={"arcs": nouveaux_arcs})

class SolutionFlot(BaseModel):
    """Encode la solution optimale du problème de flot maximal.
    Attributs:
        reseau: réseau utilisé pour le calcul.
        valeur: flot total transitant dans le réseau (milliers de m³).
        repartition: flot livré à chaque ville destination.
    """
    reseau: ReseauEau
    valeur: NonNegativeInt
    repartition: dict[str, NonNegativeInt]

    @model_validator(mode="after")
    def verifie_coherence(self) -> Self:
        if set(self.repartition.keys()) != set(self.reseau.villes):
            raise ValueError("La répartition doit couvrir exactement les villes du réseau.")
        if sum(self.repartition.values()) != self.valeur:
            raise ValueError("La somme de la répartition doit égaler la valeur du flot.")
        return self


_chemin = Path(__file__).parent / "reseau.json"
RESEAU_ADDUCTION = ReseauEau.model_validate(json.loads(_chemin.read_text()))

def capacite_infinie(reseau: ReseauEau) -> int:
    """Borne supérieure garantie : somme des capacités de tous les réservoirs.
    
    Aucun arc ne peut jamais transporter plus que ce que les sources produisent.
    On ajoute +1 pour que la borne sup de la dichotomie soit strictement hors d'atteinte.
    """
    return sum(reseau.reservoirs.values()) + 10