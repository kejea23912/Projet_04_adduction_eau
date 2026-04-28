"""Description.

Module implémentant les objets représentant le réseau d'adduction d'eau et sa solution.
"""

from typing import Self
from pydantic import BaseModel, NonNegativeInt, PositiveInt, model_validator

class Arc(BaseModel):
    """Représente une canalisation orientée entre deux nœuds avec une capacité maximale.

    Exemples:

    >>> Arc(origine="A", destination="E", capacite=7)
    Arc(origine='A', destination='E', capacite=7)
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

RESEAU_ADDUCTION = ReseauEau(
    reservoirs={"A": 15, "B": 15, "C": 15, "D": 10},
    arcs=[
        Arc(origine="A", destination="E", capacite=7),
        Arc(origine="B", destination="F", capacite=10),
        Arc(origine="B", destination="G", capacite=7),
        Arc(origine="C", destination="A", capacite=5),
        Arc(origine="C", destination="F", capacite=5),
        Arc(origine="D", destination="G", capacite=10),
        Arc(origine="E", destination="F", capacite=5),
        Arc(origine="E", destination="H", capacite=4),
        Arc(origine="E", destination="I", capacite=15),
        Arc(origine="F", destination="G", capacite=5),
        Arc(origine="F", destination="I", capacite=15),
        Arc(origine="G", destination="I", capacite=15),
        Arc(origine="H", destination="J", capacite=7),
        Arc(origine="I", destination="K", capacite=30),
        Arc(origine="I", destination="L", capacite=4),
        Arc(origine="K", destination="J", capacite=10),
    ],
    villes=["J", "K", "L"],
    capacites_villes={"J": 15, "K": 20, "L": 15},
)