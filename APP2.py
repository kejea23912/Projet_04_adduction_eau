import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import networkx as nx
    import matplotlib.pyplot as plt
    from adduction_eau.data import RESEAU_ADDUCTION
    from adduction_eau.resolution import arcs_a_ameliorer, ordre_travaux_generique, resolution
    return RESEAU_ADDUCTION, arcs_a_ameliorer, mo, nx, ordre_travaux_generique, plt, resolution


@app.cell
def _():
    POS = {
        "A": (0, 3), "B": (0, 2), "C": (0, 1), "D": (0, 0),
        "E": (2, 3), "F": (2, 1.5), "G": (2, 0),
        "H": (4, 3), "I": (4, 1.5),
        "J": (6, 2.5), "K": (6, 1.5), "L": (6, 0.5),
    }
    COULEURS = {
        "A": "#5DCAA5", "B": "#5DCAA5", "C": "#5DCAA5", "D": "#5DCAA5",
        "E": "#AFA9EC", "F": "#AFA9EC", "G": "#AFA9EC",
        "H": "#AFA9EC", "I": "#AFA9EC",
        "J": "#F0997B", "K": "#F0997B", "L": "#F0997B",
    }
    return COULEURS, POS

@app.cell
def _(COULEURS, POS, nx, plt):
    def affichage(reseau, titre, surligner=None):
        _fig, _ax = plt.subplots(figsize=(11, 5))
        G = nx.DiGraph()
        for arc in reseau.arcs:
            G.add_edge(arc.origine, arc.destination)
        nx.draw_networkx_nodes(
            G, pos=POS, nodelist=list(POS),
            node_color=[COULEURS[n] for n in POS], node_size=700, ax=_ax,
        )
        nx.draw_networkx_edges(
            G, pos=POS, ax=_ax, width=2,
            edge_color=["orange" if (u, v) in (surligner or []) else "black" for u, v in G.edges()],
        )
        nx.draw_networkx_labels(G, pos=POS, font_weight="bold", ax=_ax)
        nx.draw_networkx_edge_labels(
            G, pos=POS, ax=_ax,
            edge_labels={(a.origine, a.destination): a.capacite for a in reseau.arcs},
        )
        _ax.set_title(titre, fontweight="bold")
        _ax.axis("off")
        plt.tight_layout()
        return _ax
    return (affichage,)


@app.cell
def _(RESEAU_ADDUCTION, affichage, mo, resolution):
    mo.vstack([
        mo.md("# Interface — Adduction d'eau"),
        mo.callout(
            mo.md(f"**Flot actuel : {resolution(RESEAU_ADDUCTION).valeur} milliers m³/jour**"),
            kind="info",
        ),
        affichage(RESEAU_ADDUCTION, "Réseau initial — capacités des arcs"),
    ])



@app.cell
def _(mo):
    mo.md("---\n## Étape 1 — Quels arcs améliorer ?")


@app.cell
def _(RESEAU_ADDUCTION, arcs_a_ameliorer, mo):
    btn_analyse = mo.ui.button(
        on_click=lambda _: arcs_a_ameliorer(RESEAU_ADDUCTION),
        value=None,
        label="Calculer les propositions d'amélioration",
    )
    btn_analyse


@app.cell
def _(btn_analyse, mo):
    mo.stop(btn_analyse.value is None, mo.md("_Cliquez sur le bouton pour analyser le réseau._"))
    solution = btn_analyse.value
    mo.callout(
        mo.md(
            f"**{len(solution.propositions)} arc(s) à améliorer** — "
            f"flot actuel : **{solution.flot_actuel}** → flot théorique : **{solution.flot_theorique}** "
            f"(+{solution.gain_flot} milliers m³/j)"
        ),
        kind="warn",
    )
    return (solution,)



@app.cell
def _(mo):
    mo.md("---\n## Étape 2 — Choisissez les arcs à modifier")


@app.cell
def _(mo, solution):
    selecteur = mo.ui.multiselect(
        options={
            f"{p.origine}→{p.destination}  (cap : {p.capacite_actuelle} → {p.capacite_requise},  +{p.gain})": p
            for p in solution.propositions
        },
        label="Sélectionnez les arcs à améliorer (5 maximum)",
    )
    selecteur
    return (selecteur,)


@app.cell
def _(RESEAU_ADDUCTION, affichage, mo, selecteur):
    mo.stop(not selecteur.value, mo.md("_Sélectionnez au moins un arc ci-dessus._"))
    choix = selecteur.value[:5]
    affichage(
        RESEAU_ADDUCTION,
        f"{len(choix)} arc(s) sélectionné(s) — en orange",
        surligner=[(p.origine, p.destination) for p in choix],
    )
    return (choix,)


@app.cell
def _(mo):
    mo.md("---\n## Étape 3 — Ordre optimal des travaux")


@app.cell
def _(RESEAU_ADDUCTION, choix, mo, ordre_travaux_generique):
    btn_ordre = mo.ui.button(
        on_click=lambda _: ordre_travaux_generique(RESEAU_ADDUCTION, choix),
        value=None,
        label="Calculer l'ordre optimal des travaux",
    )
    btn_ordre


@app.cell
def _(RESEAU_ADDUCTION, btn_ordre, mo, resolution):
    mo.stop(btn_ordre.value is None, mo.md("_Cliquez sur le bouton pour calculer l'ordre._"))
    etapes = btn_ordre.value
    _flot_depart = resolution(RESEAU_ADDUCTION).valeur
    _precedent = _flot_depart
    _lignes = []
    for _i, (_prop, _flot) in enumerate(etapes, 1):
        _lignes.append(
            f"| {_i} | **{_prop.origine}→{_prop.destination}** "
            f"| {_prop.capacite_actuelle} → {_prop.capacite_requise} "
            f"| **{_flot}** (+{_flot - _precedent}) |"
        )
        _precedent = _flot
    mo.vstack([
        mo.callout(
            mo.md(
                f"Flot de départ : **{_flot_depart}** → Flot final : **{etapes[-1][1]}** "
                f"milliers m³/j  (+{etapes[-1][1] - _flot_depart})"
            ),
            kind="success",
        ),
        mo.md(
            "| Étape | Arc | Capacité | Flot après travaux |\n"
            "|-------|-----|----------|--------------------|\n"
            + "\n".join(_lignes)
        ),
    ])


if __name__ == "__main__":
    app.run()