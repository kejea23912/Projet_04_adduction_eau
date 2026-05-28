# 💧 adduction-eau

<p align="center">
  <img src="https://img.shields.io/badge/python-3.13%2B-blue?style=flat-square&logo=python" alt="Python 3.13+"/>
  <img src="https://img.shields.io/badge/networkx-Dinic-purple?style=flat-square" alt="NetworkX"/>
  <img src="https://img.shields.io/badge/CLI-Typer-orange?style=flat-square" alt="Typer"/>
  <img src="https://img.shields.io/badge/tests-pytest-yellow?style=flat-square&logo=pytest" alt="pytest"/>
</p>

<p align="center">
  <b>Résolution du problème d'adduction d'eau par flot maximal — en ligne de commande.</b>
</p>

---

**adduction-eau** est un outil CLI avec une interface graphique en Python pour analyser et optimiser un réseau de distribution d'eau.  
Il calcule le **flot maximal** d'un réseau de canalisations, identifie les **goulots d'étranglement**, détermine les capacités à rénover, et ordonne les travaux pour maximiser le gain à chaque étape.

Le tout avec une sortie terminal et une interface de commandes fluide via [Typer](https://typer.tiangolo.com), et une interface graphique via [Marimo](https://marimo.io)
---

## ✨ Fonctionnalités de l'interface de commandes

- 📊 **Flot actuel** — calcule le flot maximal du réseau historique et affiche la répartition par ville
- 🔧 **ameliorationregion** — détermine les nouvelles capacités à prévoir pour les arcs critiques (`A→E` et `I→L`)
- 🏗️ **Ordre des travaux** — trouve l'ordre optimal de réfection pour maximiser le gain à chaque étape
- 🧩 **Modèle de données validé** — modèles Pydantic robustes avec vérification de cohérence
- 🔬 **Interface graphique** — notebook [Marimo](https://marimo.io) pour une resolution générale
- ✅ **Tests complets** — suite pytest couvrant données, résolution et optimisation

---

## 📦 Installation

```bash
# Cloner le dépôt
git clone https://github.com/votre-utilisateur/adduction-eau.git
cd adduction-eau

# Installer avec uv (recommandé)
uv sync

# Ou avec pip
pip install -e .
```

> **Pré-requis :** Python 3.13+

---

## 🚀 Utilisation

### Voir le flot actuel

```bash
uv run adduction-eau flot-actuel
```

```
Flot maximal actuel : 37 milliers de m3/ jour

 Repartition par ville
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Ville  ┃ Flot reçu (milliers m3)  ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ J      │ 14                       │
│ K      │ 20                       │
│ L      │ 3                        │
└────────┴──────────────────────────┘
```

---

### Calculer les capacités optimales

```bash
uv run adduction-eau ameliorationregion
```

```
Capacités à prévoir pour les réfections :
  Arc A→E : 19 milliers de m³/jour
  Arc I→L : 15 milliers de m³/jour

Nouveau flot optimal : 49 milliers de m³/jour
```

---

### Déterminer l'ordre optimal des travaux

```bash
uv run adduction-eau travaux
```

```
Ordre optimal des travaux :

  Étape 1 — Réfection A→E (cap=19)
           → Flot après travaux : 44 milliers de m³/jour

  Étape 2 — Réfection I→L (cap=15)
           → Flot après travaux : 49 milliers de m³/jour
```
---
### Déterminer les travaux sans aucune conditions

```
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Ordre ┃ Flot reçu (milliers m3)  ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   1   │ 14                       │
│   2   │ 20                       │
│   3   │ 3                        │
└───────┴──────────────────────────┘
```
---

### Aide

```bash
adduction-eau --help
```

```
 Usage: adduction-eau [OPTIONS] COMMAND [ARGS]...

 Résolution du problème d'adduction d'eau.

╭─ Options ──────────────────────────────────────────────╮
│ --help   Show this message and exit.                   │
╰────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────╮
│ flot-actuel          Affiche le flot maximal du réseau                                │
│ ameliorationregion   Détermine les nouvelles capacités                                │
│ travaux              Détermine l'ordre optimal de réfection                           │
│ optimisation         propose les amélioration optimales pour ateindre le flot maximal │
╰───────────────────────────────────────────────────────────────────────────────────────╯
" optimisation " est un commande supplémentaire a ce que les consigne demendait, il montre les
vraie traveau optimal a faire por ateindre les flot maximal. l'idée est que peut inporte la
capacité des réseau il va ouffrir les traveaux optimal 
```

---
## 🗺️ Architecture du réseau

Le réseau modélisé est un graphe orienté avec :

- **4 réservoirs** (nœuds sources) : `A`, `B`, `C`, `D`
- **5 nœuds intermédiaires** : `E`, `F`, `G`, `H`, `I`
- **3 villes destinatrices** (puits) : `J`, `K`, `L`
- **16 canalisations** avec des capacités en milliers de m³/jour

L'algorithme de **Dinic** (via [NetworkX](https://networkx.org)) résout le flot maximal entre une super-source virtuelle et un super-puits virtuel.

```
A ──────────► E ──► H ──► J
B ──► F ──────────► I ──► K
C ──────────────────────► L
D ──► G
```

---

## 🧪 Tests

```bash
# Lancer tous les tests
uv run pytest

# Avec verbosité
uv run pytest -v
```

Les tests couvrent :

- Validation des modèles `Arc`, `ReseauEau`, `SolutionFlot`
- Construction du graphe (super-source, super-puits, arcs)
- Valeur du flot actuel (37 milliers de m³/jour)
- Capacités optimales calculées (`A→E = 19`, `I→L = 15`, flot = 49)
- Ordre optimal des travaux (`A→E` en premier)

---

## 🏗️ Structure du projet

```
adduction-eau/
├── src/
│   └── adduction_eau/
│       ├── APP2.py         # interface graphique   
│       ├── app.py          # Interface CLI (Typer + Rich)
│       ├── data.py         # Modèles Pydantic (Arc, ReseauEau, SolutionFlot)
│       └── resolution.py   # Algorithme de flot maximal (NetworkX / Dinic)
├── tests/
│   ├── test_data.py        # Tests des modèles de données
│   └── test_resolution.py  # Tests de la résolution et de l'optimisation
├── pyproject.toml 
└── README.md
```

---
## APP2.py 
Il s’agit d’une interface graphique supplémentaire qui nous aide à résoudre les problèmes du réseau, quelle que soit la configuration des ARC.
Concrètement, dans DATA.py, vous pouvez personnaliser librement le réseau, et grâce à cette interface, vous trouverez toujours une solution d’amélioration.

```bash
# Lancer l'interface interactif
uv run marimo run src\adduction_eau\APP2.py
```
### utilisation

- Etape 1 
<img width="2584" height="972" alt="Image" src="https://github.com/user-attachments/assets/ac9e41de-cac2-4f6b-b667-f89290c598b8" />

Cliquer sur le bouton Calculer les propositions d’amélioration.
Ce bouton calcule toutes les améliorations possibles, quelle que
soit la configuration du réseau.

- Etape 2 

 Sélectionnez les arcs à modifier parmi ceux proposés par le programme.

- Etape 3

Puis calculez l’ordre optimal des travaux, qui dépendra de votre choix précédent, afin de vous guider dans leur réalisation

---

## 🧩 Dépendances

| Bibliothèque | Rôle |
|---|---|
| [networkx](https://networkx.org) | Algorithme de flot maximal (Dinic) |
| [pydantic](https://docs.pydantic.dev) | Modélisation et validation des données |
| [typer](https://typer.tiangolo.com) | Interface en ligne de commande |
| [marimo](https://marimo.io) | Notebook interactif |
| [matplotlib](https://matplotlib.org) | Visualisation du réseau |
| [pytest](https://pytest.org) | Tests unitaires |

---


Fait par **Kenny Jean-elie** et **Ndèye Fatou DIOP**