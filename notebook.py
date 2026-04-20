import marimo

__generated_with = "0.23.1"
app = marimo.App(width="wide")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import networkx as nx
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import io
    import base64

    return base64, io, mpatches, nx, plt


@app.cell
def _(mo):
    mo.md("""
    # Sujet 04 — Adduction d'eau
    ## Résolution des 3 questions

    Trois villes **J, K, L** sont alimentées par quatre réserves **A, B, C, D**
    via un réseau passant par des noeuds intermédiaires **E, F, G, H, I**.

    | Réserve | Stock journalier |
    |---------|-----------------|
    | A, B, C | 15 milliers m³/j |
    | D       | 10 milliers m³/j |

    **Demandes futures :** J = 15k, K = 20k, L = 15k m³/j
    """)
    return


@app.cell
def _():
    # Positions fixes des noeuds (sans S et T)
    POS = {
        "A": (0, 3),   "B": (0, 2),   "C": (0, 1),   "D": (0, 0),
        "E": (2, 3),   "F": (2, 1.5), "G": (2, 0),
        "H": (4, 3),   "I": (4, 1.5),
        "J": (6, 2.5), "K": (6, 1.5), "L": (6, 0.5),
    }

    # Couleurs par catégorie
    COULEURS = {
        "A": "#5DCAA5", "B": "#5DCAA5", "C": "#5DCAA5", "D": "#5DCAA5",
        "E": "#AFA9EC", "F": "#AFA9EC", "G": "#AFA9EC",
        "H": "#AFA9EC", "I": "#AFA9EC",
        "J": "#F0997B", "K": "#F0997B", "L": "#F0997B",
    }
    TEXTE = {
        "A": "#085041", "B": "#085041", "C": "#085041", "D": "#085041",
        "E": "#3C3489", "F": "#3C3489", "G": "#3C3489",
        "H": "#3C3489", "I": "#3C3489",
        "J": "#712B13", "K": "#712B13", "L": "#712B13",
    }
    return COULEURS, POS, TEXTE


@app.cell
def _(COULEURS, POS, TEXTE, base64, io, mpatches, plt):
    def dessine(arcs, flot_dict, titre, montrer_flot=False):
        fig, ax = plt.subplots(figsize=(11, 5))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        noeuds = list(POS.keys())

        # Nœuds
        for n in noeuds:
            x, y = POS[n]
            cercle = plt.Circle((x, y), 0.28, color=COULEURS[n], zorder=3)
            ax.add_patch(cercle)
            ax.text(x, y, n, ha="center", va="center",
                    fontsize=11, fontweight="bold",
                    color=TEXTE[n], zorder=4)

        # Arcs
        for (u, v), cap in arcs.items():
            if u not in POS or v not in POS:
                continue
            x1, y1 = POS[u]
            x2, y2 = POS[v]

            flot = flot_dict.get(u, {}).get(v, 0) if flot_dict else 0
            sature = flot >= cap and cap > 0

            # Décalage léger pour éviter superposition sur arcs parallèles
            dx, dy = x2 - x1, y2 - y1
            norm = (dx**2 + dy**2)**0.5
            px, py = -dy / norm * 0.08, dx / norm * 0.08

            ax.annotate("", xy=(x2 - dx/norm*0.3, y2 - dy/norm*0.3),
                        xytext=(x1 + dx/norm*0.3, y1 + dy/norm*0.3),
                        arrowprops=dict(
                            arrowstyle="-|>",
                            color="black" if sature else "#aaaaaa",
                            lw=1.8 if sature else 1.0,
                        ), zorder=2)

            # Label capacité au milieu de l'arc
            mx, my = (x1 + x2) / 2 + px, (y1 + y2) / 2 + py
            valeur = f"{int(flot)}" if montrer_flot else str(int(cap))
            ax.text(mx, my, valeur, ha="center", va="center",
                    fontsize=8, color="#333333",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white",
                              ec="none", alpha=0.85), zorder=5)

        # Légende
        legende = [
            mpatches.Patch(color="#5DCAA5", label="Réserves (A,B,C,D)"),
            mpatches.Patch(color="#AFA9EC", label="Intermédiaires (E,F,G,H,I)"),
            mpatches.Patch(color="#F0997B", label="Villes (J,K,L)"),
        ]
        ax.legend(handles=legende, loc="lower right", fontsize=8, framealpha=0.9)
        ax.set_title(titre, fontsize=12, fontweight="bold", pad=10)
        ax.set_xlim(-0.6, 6.8)
        ax.set_ylim(-0.6, 3.6)
        ax.axis("off")
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=130, bbox_inches="tight")
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()

    return (dessine,)


@app.cell
def _(mo):
    mo.md("""
    ---
    ## Question 1 — Flot maximal du réseau actuel
    """)
    return


@app.cell
def _(nx):
    ARCS_ACTUELS = {
        ("A", "E"): 7,  ("B", "F"): 10, ("B", "G"): 7,
        ("C", "A"): 5,  ("C", "F"): 5,  ("D", "G"): 10,
        ("E", "F"): 5,  ("E", "H"): 4,  ("E", "I"): 15,
        ("F", "G"): 5,  ("F", "I"): 15, ("G", "I"): 15,
        ("H", "J"): 7,  ("I", "K"): 30, ("I", "L"): 4, ("K", "J"): 10,
    }
    # Source/puits virtuels pour le calcul uniquement
    _arcs_calc = dict(ARCS_ACTUELS)
    _arcs_calc[("S", "A")] = 15
    _arcs_calc[("S", "B")] = 15
    _arcs_calc[("S", "C")] = 15
    _arcs_calc[("S", "D")] = 10
    _arcs_calc[("J", "T")] = 15
    _arcs_calc[("K", "T")] = 20
    _arcs_calc[("L", "T")] = 15

    _G = nx.DiGraph()
    for (_u, _v), _c in _arcs_calc.items():
        _G.add_edge(_u, _v, capacity=_c)

    valeur_q1, flot_q1 = nx.maximum_flow(_G, "S", "T")
    j_q1 = flot_q1["J"]["T"]
    k_q1 = flot_q1["K"]["T"]
    l_q1 = flot_q1["L"]["T"]
    return ARCS_ACTUELS, flot_q1, j_q1, k_q1, l_q1, valeur_q1


@app.cell
def _(ARCS_ACTUELS, dessine, mo):
    _img = dessine(ARCS_ACTUELS, None, "Réseau actuel — capacités des arcs")
    mo.vstack([
        mo.md("### Graphe du réseau actuel (capacités)"),
        mo.Html(f'<img src="data:image/png;base64,{_img}" style="width:100%"/>'),
    ])
    return


@app.cell
def _(ARCS_ACTUELS, dessine, flot_q1, j_q1, k_q1, l_q1, mo, valeur_q1):
    _img = dessine(ARCS_ACTUELS, flot_q1,
                   "Réseau actuel — flot optimal (arcs noirs = saturés)",
                   montrer_flot=True)
    mo.vstack([
        mo.callout(mo.md(f"**Flot maximal actuel = {int(valeur_q1)} milliers m³/jour**"), kind="info"),
        mo.md(f"""
    | Ville | Flot reçu | Demande | Écart |
    |-------|-----------|---------|-------|
    | J | {int(j_q1)} | 15 | {int(j_q1)-15} |
    | K | {int(k_q1)} | 20 | {int(k_q1)-20} |
    | L | {int(l_q1)} | 15 | {int(l_q1)-15} |

    Le flot est insuffisant. La région décide de rénover **(AE)** et **(IL)**.
        """),
        mo.md("### Graphe du réseau actuel (flots optimaux)"),
        mo.Html(f'<img src="data:image/png;base64,{_img}" style="width:100%"/>'),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ---
    ## Question 2 — Capacités à prévoir pour (AE) et (IL)
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Analyse des goulots

    **Ville J :** ne reçoit que depuis deux chemins :
    - E → H → J : limité par **E→H = 4** (arc fixe)
    - I → K → J : limité par **K→J = 10** (arc fixe)
    - **J max = 4 + 10 = 14**, indépendamment de (AE) et (IL)

    **Ville L :** ne reçoit que depuis I → L.
    Avec AE=7, E n'envoie que 3 vers I, donc L reste bloquée à 3.
    Il faut d'abord augmenter **(AE)** pour libérer du débit vers I.

    **Capacités retenues :**
    - **(AE) = 20** — permet à E de saturer E→I (15) et E→H (4)
    - **(IL) = 15** — satisfait la demande de L
    """)
    return


@app.cell
def _(nx):
    ARCS_RENOVES = {
        ("A", "E"): 20, ("B", "F"): 10, ("B", "G"): 7,
        ("C", "A"): 5,  ("C", "F"): 5,  ("D", "G"): 10,
        ("E", "F"): 5,  ("E", "H"): 4,  ("E", "I"): 15,
        ("F", "G"): 5,  ("F", "I"): 15, ("G", "I"): 15,
        ("H", "J"): 7,  ("I", "K"): 30, ("I", "L"): 15, ("K", "J"): 10,
    }
    _arcs_calc = dict(ARCS_RENOVES)
    _arcs_calc[("S", "A")] = 15
    _arcs_calc[("S", "B")] = 15
    _arcs_calc[("S", "C")] = 15
    _arcs_calc[("S", "D")] = 10
    _arcs_calc[("J", "T")] = 15
    _arcs_calc[("K", "T")] = 20
    _arcs_calc[("L", "T")] = 15

    _G = nx.DiGraph()
    for (_u, _v), _c in _arcs_calc.items():
        _G.add_edge(_u, _v, capacity=_c)

    valeur_q2, flot_q2 = nx.maximum_flow(_G, "S", "T")
    j_q2 = flot_q2["J"]["T"]
    k_q2 = flot_q2["K"]["T"]
    l_q2 = flot_q2["L"]["T"]
    return ARCS_RENOVES, flot_q2, j_q2, k_q2, l_q2, valeur_q2


@app.cell
def _(
    ARCS_RENOVES,
    dessine,
    flot_q2,
    j_q2,
    k_q2,
    l_q2,
    mo,
    valeur_q1,
    valeur_q2,
):
    _img = dessine(ARCS_RENOVES, flot_q2,
                   "Réseau rénové AE=20, IL=15 — flot optimal",
                   montrer_flot=True)
    mo.vstack([
        mo.callout(mo.md(
            f"**Nouveau flot = {int(valeur_q2)} milliers m³/jour** "
            f"(+{int(valeur_q2-valeur_q1)} par rapport au réseau actuel)"
        ), kind="success"),
        mo.md(f"""
    | Ville | Flot reçu | Demande | Satisfaite ? |
    |-------|-----------|---------|-------------|
    | J | {int(j_q2)} | 15 | Goulot structurel E→H=4 |
    | K | {int(k_q2)} | 20 | Oui |
    | L | {int(l_q2)} | 15 | Oui |
        """),
        mo.md("### Graphe du réseau rénové"),
        mo.Html(f'<img src="data:image/png;base64,{_img}" style="width:100%"/>'),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ---
    ## Question 3 — Ordre optimal des travaux
    """)
    return


@app.cell
def _(nx):
    def flot_scenario(cap_ae, cap_il):
        _arcs = {
            ("A", "E"): cap_ae, ("B", "F"): 10, ("B", "G"): 7,
            ("C", "A"): 5,  ("C", "F"): 5,  ("D", "G"): 10,
            ("E", "F"): 5,  ("E", "H"): 4,  ("E", "I"): 15,
            ("F", "G"): 5,  ("F", "I"): 15, ("G", "I"): 15,
            ("H", "J"): 7,  ("I", "K"): 30, ("I", "L"): cap_il, ("K", "J"): 10,
            ("S", "A"): 15, ("S", "B"): 15, ("S", "C"): 15, ("S", "D"): 10,
            ("J", "T"): 15, ("K", "T"): 20, ("L", "T"): 15,
        }
        _G = nx.DiGraph()
        for (_u, _v), _c in _arcs.items():
            _G.add_edge(_u, _v, capacity=_c)
        _val, _fd = nx.maximum_flow(_G, "S", "T")
        return int(_val), int(_fd["J"]["T"]), int(_fd["K"]["T"]), int(_fd["L"]["T"])

    t0,  j0,  k0,  l0  = flot_scenario(7,  4)
    tA1, jA1, kA1, lA1 = flot_scenario(7,  15)
    tA2, jA2, kA2, lA2 = flot_scenario(20, 15)
    tB1, jB1, kB1, lB1 = flot_scenario(20, 4)
    tB2, jB2, kB2, lB2 = flot_scenario(20, 15)
    return j0, jA1, jB1, k0, kA1, kB1, l0, lA1, lB1, t0, tA1, tA2, tB1, tB2


@app.cell
def _(j0, jA1, jB1, k0, kA1, kB1, l0, lA1, lB1, mo, t0, tA1, tA2, tB1, tB2):
    mo.vstack([
        mo.md(f"""
    ### Comparaison des deux ordres

    | | Option A — IL d'abord | Option B — AE d'abord |
    |---|---|---|
    | **Départ** | Flot={t0} · J={j0} K={k0} L={l0} | Flot={t0} · J={j0} K={k0} L={l0} |
    | **Étape 1** | IL=15, AE=7 → Flot=**{tA1}** · J={jA1} K={kA1} L={lA1} | AE=20, IL=4 → Flot=**{tB1}** · J={jB1} K={kB1} L={lB1} |
    | **Gain étape 1** | +{tA1-t0} | +{tB1-t0} |
    | **Étape 2** | AE=20 → Flot=**{tA2}** | IL=15 → Flot=**{tB2}** |
    | **Gain étape 2** | +{tA2-tA1} | +{tB2-tB1} |
        """),
        mo.callout(mo.md(f"""
    **Ordre optimal : (AE) en premier, puis (IL)**

    Rénover (IL) en premier n'apporte rien (+{tA1-t0}) car avec AE=7,
    E n'envoie que 3 vers I — L reste bloquée à {lA1}.

    En rénovant (AE) d'abord, E envoie davantage vers I dès l'étape 1 (+{tB1-t0}),
    ce qui rend la rénovation de (IL) pleinement efficace à l'étape 2 (+{tB2-tB1}).
        """), kind="success"),
    ])
    return


if __name__ == "__main__":
    app.run()
