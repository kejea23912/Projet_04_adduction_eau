"""Description.

Interface en ligne de commande pour résoudre le problème d'adduction d'eau créer avec Typer

"""

import typer

from adduction_eau.data import RESEAU_ADDUCTION
from adduction_eau.resolution import capacites_optimales, ordre_travaux, resolution

app = typer.Typer()
console = Console()

@app.command()
def flot_actuel() -> None:
    """ Afiche le flot maximal du réseau historique"""

if __name__ == "__main__":
    app()

