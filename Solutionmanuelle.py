# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "matplotlib>=3.10.8",
#     "networkx>=3.6.1",
#     "pydantic>=2.12.5",
# ]
# ///

import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import networkx as nx
    import matplotlib.pyplot as plt
    from src.adduction_eau.data import RESEAU_ADDUCTION
    return RESEAU_ADDUCTION, mo, nx, plt


@app.cell
def _():
    POS = {
        "A": (0, 3),   "B": (0, 2),   "C": (0, 1),   "D": (0, 0),
        "E": (2, 3),   "F": (2, 1.5), "G": (2, 0),
        "H": (4, 3),   "I": (4, 1.5),
        "J": (6, 2.5), "K": (6, 1.5), "L": (6, 0.5),
    }
    COULEURS = {
        "A": "#5DCAA5", "B": "#5DCAA5", "C": "#5DCAA5", "D": "#5DCAA5",
        "E": "#AFA9EC", "F": "#AFA9EC", "G": "#AFA9EC",
        "H": "#AFA9EC", "I": "#AFA9EC",
        "J": "#F0997B", "K": "#F0997B", "L": "#F0997B",
    }
    DEMANDES = {"J": 15, "K": 20, "L": 15}
    return COULEURS, DEMANDES, POS


@app.cell
def _(DEMANDES, RESEAU_ADDUCTION, nx):
    def construit_graphe(reseau, demandes):
        """Construit un DiGraph avec super-source S et super-puits T plafonné par les demandes."""
        graphe = nx.DiGraph()
        for noeud, cap in reseau.reservoirs.items():
            graphe.add_edge("S", noeud, capacite=cap)
        for arc in reseau.arcs:
            graphe.add_edge(arc.origine, arc.destination, capacite=arc.capacite)
        for ville, dem in demandes.items():
            graphe.add_edge(ville, "T", capacite=dem)
        return graphe

    return (construit_graphe,)


@app.cell
def _(COULEURS, POS, nx, plt):
    def affichage(reseau, titre, flot=None):
        """Dessine le réseau avec nx.draw_networkx. Affiche les capacités ou les flots."""
        _fig, _rep = plt.subplots(figsize=(11, 5))

        G = nx.DiGraph()
        for arc in reseau.arcs:
            G.add_edge(arc.origine, arc.destination, capacite=arc.capacite)

        noeuds = list(POS.keys())
        nx.draw_networkx_nodes(
            G, pos=POS, nodelist=noeuds,
            node_color=[COULEURS[n] for n in noeuds],
            node_size=700, ax=_rep,
        )
        nx.draw_networkx_edges(G, pos=POS, ax=_rep)
        nx.draw_networkx_labels(G, pos=POS, font_weight="bold", ax=_rep)

        if flot is None:
            labels = {(a.origine, a.destination): a.capacite for a in reseau.arcs}
        else:
            labels = {
                (a.origine, a.destination): f"{flot.get(a.origine, {}).get(a.destination, 0)} : {a.capacite}"
                for a in reseau.arcs
            }

        nx.draw_networkx_edge_labels(G, pos=POS, edge_labels=labels, ax=_rep)
        _rep.set_title(titre, fontweight="bold")
        _rep.axis("off")
        plt.tight_layout()
        return _rep

    return (affichage,)


@app.cell
def _(mo):
    mo.md(r"""
    # Sujet 04 — Adduction d'eau

    Trois villes **J, K, L** sont alimentées par quatre réserves **A, B, C, D**
    via des nœuds intermédiaires **E, F, G, H, I**.

    | Réserve | Stock journalier |
    |---------|-----------------|
    | A, B, C | 15 milliers m³/j |
    | D       | 10 milliers m³/j |

    **Demandes futures :** J = 15k, K = 20k, L = 15k m³/j
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    
    """)
    return


@app.cell
def _(DEMANDES, RESEAU_ADDUCTION, construit_graphe, nx):
    _G = construit_graphe(RESEAU_ADDUCTION, DEMANDES)
    valeur_q1, flot_q1 = nx.algorithms.flow.maximum_flow(
        flowG=_G, _s="S", _t="T", capacity="capacite"
    )
    valeur_q1 = int(valeur_q1)
    return flot_q1, valeur_q1


@app.cell
def _(RESEAU_ADDUCTION, affichage):
    affichage(RESEAU_ADDUCTION, "Réseau actuel — capacités des arcs")


@app.cell
def _(DEMANDES, RESEAU_ADDUCTION, affichage, flot_q1, mo, valeur_q1):
    mo.vstack([
        mo.callout(mo.md(f"**Flot maximal actuel = {valeur_q1} milliers m³/jour**"), kind="info"),
        mo.md(f"""
| Ville | Flot reçu | Demande | Écart |
|-------|-----------|---------|-------|
| J | {flot_q1['J']['T']} | {DEMANDES['J']} | {flot_q1['J']['T'] - DEMANDES['J']} |
| K | {flot_q1['K']['T']} | {DEMANDES['K']} | {flot_q1['K']['T'] - DEMANDES['K']} |
| L | {flot_q1['L']['T']} | {DEMANDES['L']} | {flot_q1['L']['T'] - DEMANDES['L']} |

Le flot est insuffisant. La région décide de rénover **(A→E)** et **(I→L)**.
        """),
        affichage(RESEAU_ADDUCTION, "Réseau actuel — flots optimaux (format : flot : capacité)", flot=flot_q1),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
 

    **Analyse des goulots :**

    - La ville **J** reçoit via E→H→J (limité par **E→H = 4**) et via I→K→J.
      Son maximum structurel est donc **J ≤ 4 + 10 = 14**, indépendamment de (A→E) et (I→L).
    - La ville **L** reçoit uniquement via I→L. Avec A→E = 7, E ne peut envoyer que 3 vers I.
      Il faut d'abord augmenter **(A→E)** pour libérer du débit vers I, puis augmenter **(I→L)**.

    **Capacités retenues :** **(A→E) = 20** et **(I→L) = 15**
    """)
    return


@app.cell
def _(DEMANDES, RESEAU_ADDUCTION, construit_graphe, nx):
    reseau_renove = (
        RESEAU_ADDUCTION
        .avec_arc_modifie("A", "E", 20)
        .avec_arc_modifie("I", "L", 15)
    )
    _G = construit_graphe(reseau_renove, DEMANDES)
    valeur_q2, flot_q2 = nx.algorithms.flow.maximum_flow(
        flowG=_G, _s="S", _t="T", capacity="capacite"
    )
    valeur_q2 = int(valeur_q2)
    return flot_q2, reseau_renove, valeur_q2


@app.cell
def _(DEMANDES, affichage, flot_q2, mo, reseau_renove, valeur_q1, valeur_q2):
    mo.vstack([
        mo.callout(mo.md(
            f"**Nouveau flot = {valeur_q2} milliers m³/jour** "
            f"(+{valeur_q2 - valeur_q1} par rapport au réseau actuel)"
        ), kind="success"),
        mo.md(f"""
| Ville | Flot reçu | Demande | Satisfaite ? |
|-------|-----------|---------|-------------|
| J | {flot_q2['J']['T']} | {DEMANDES['J']} | Non — goulot structurel E→H = 4 |
| K | {flot_q2['K']['T']} | {DEMANDES['K']} | Oui ✓ |
| L | {flot_q2['L']['T']} | {DEMANDES['L']} | Oui ✓ |
        """),
        affichage(reseau_renove, "Réseau rénové (A→E=20, I→L=15) — flots optimaux", flot=flot_q2),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
   
    """)
    return


@app.cell
def _(DEMANDES, RESEAU_ADDUCTION, construit_graphe, nx):
    def flot_scenario(cap_ae, cap_il):
        """Calcule le flot total pour des capacités données sur A→E et I→L."""
        reseau = (
            RESEAU_ADDUCTION
            .avec_arc_modifie("A", "E", cap_ae)
            .avec_arc_modifie("I", "L", cap_il)
        )
        G = construit_graphe(reseau, DEMANDES)
        valeur, _ = nx.algorithms.flow.maximum_flow(
            flowG=G, _s="S", _t="T", capacity="capacite"
        )
        return int(valeur)

    flot_depart        = flot_scenario(7,  4)  
    flot_ae_en_premier = flot_scenario(20, 4)   
    flot_il_en_premier = flot_scenario(7,  15)  
    flot_final         = flot_scenario(20, 15)  
    return flot_ae_en_premier, flot_depart, flot_final, flot_il_en_premier, flot_scenario


@app.cell
def _(flot_ae_en_premier, flot_depart, flot_final, flot_il_en_premier, mo):
    mo.vstack([
        mo.md(f"""
### Comparaison des deux ordres

| | Option A — A→E d'abord | Option B — I→L d'abord |
|---|---|---|
| **Départ** | Flot = {flot_depart} | Flot = {flot_depart} |
| **Après étape 1** | A→E=20, I→L=4 → Flot = **{flot_ae_en_premier}** | I→L=15, A→E=7 → Flot = **{flot_il_en_premier}** |
| **Gain étape 1** | +{flot_ae_en_premier - flot_depart} | +{flot_il_en_premier - flot_depart} |
| **Après étape 2** | I→L=15 → Flot = **{flot_final}** | A→E=20 → Flot = **{flot_final}** |
| **Gain étape 2** | +{flot_final - flot_ae_en_premier} | +{flot_final - flot_il_en_premier} |
        """),
        mo.callout(mo.md(f"""
**Ordre optimal : (A→E) en premier, puis (I→L)**

Rénover (I→L) en premier n'apporte rien (+{flot_il_en_premier - flot_depart}) car avec A→E = 7,
le nœud E ne peut envoyer que 3 vers I — L reste bloquée.

En rénovant (A→E) d'abord, E envoie davantage vers I dès l'étape 1 (+{flot_ae_en_premier - flot_depart}),
ce qui rend la rénovation de (I→L) pleinement efficace (+{flot_final - flot_ae_en_premier}).
        """), kind="success"),
    ])
    return


if __name__ == "__main__":
    app.run()