"""Description.

Interface en ligne de commande pour résoudre le problème d'adduction d'eau créer avec Typer

"""

import typer
from adduction_eau.data import RESEAU_ADDUCTION
from adduction_eau.resolution import capacites_optimales, ordre_travaux, resolution
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Résolution du problème d'adduction d'eau.")
console = Console()

@app.command()
def flot_actuel() -> None:
    """ Afiche le flot maximal du réseau historique"""
    sol = resolution(RESEAU_ADDUCTION)

    console.print(f"\n[bold]Flot maximal actuel :[/bold] {sol.valeur} milliers de m3/ jour\n")

    table = Table(title="Repartition par ville")
    table.add_column("Ville", style="cyan")
    table.add_column("Flot reçu (milliers m3)", justify="right")
    for ville, flot in sol.repartition.items():
        table.add_row(ville, str(flot))
    console.print(table)

@app.command()
def amelioration() -> None:
    """Détermine les nouvelles capacités à prévoir pour A→E et I→L."""
    cap_ae, cap_il, flot_optimal = capacites_optimales(RESEAU_ADDUCTION)
 
    console.print("\n[bold]Capacités à prévoir pour les réfections :[/bold]")
    console.print(f"  Arc A→E : [green]{cap_ae}[/green] milliers de m³/jour")
    console.print(f"  Arc I→L : [green]{cap_il}[/green] milliers de m³/jour")
    console.print(f"\n[bold]Nouveau flot optimal :[/bold] {flot_optimal} milliers de m³/jour\n")
 
 
@app.command()
def travaux() -> None:
    """Détermine l'ordre optimal de réfection des canalisations."""
    cap_ae, cap_il, _ = capacites_optimales(RESEAU_ADDUCTION)
    etapes = ordre_travaux(RESEAU_ADDUCTION, cap_ae, cap_il)
 
    console.print("\n[bold]Ordre optimal des travaux :[/bold]\n")
    for i, (description, flot) in enumerate(etapes, start=1):
        console.print(f"  Étape {i} — {description}")
        console.print(f"           → Flot après travaux : [green]{flot}[/green] milliers de m³/jour\n")
 

if __name__ == "__main__":
    app()

