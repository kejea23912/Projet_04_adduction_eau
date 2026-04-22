"""Description.

Interface en ligne de commande pour résoudre le problème d'adduction d'eau créer avec Typer

"""

import typer
from adduction_eau.data import RESEAU_ADDUCTION
from adduction_eau.resolution import capacites_optimales, ordre_travaux, resolution
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def flot_actuel() -> None:
    """ Afiche le flot maximal du réseau historique"""
    sol = resolution(RESEAU_ADDUCTION)

    console.print(f"\n[bold] flot maximal actuel : [/bold] {sol.valeur} milliers de m3/ jour\n")

    table = Table(table="Repartition par ville")
    table.add_column("Ville", style="cyan")
    table.add_column("Flot reçu (milliers m3)", justify="right")
    for ville, flot in sol.repartition.items():
        table.add_row(ville, str(flot))
    console.print(table)



if __name__ == "__main__":
    app()

