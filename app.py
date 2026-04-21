import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #Problème d'adduction d'eau
    iterface graphique et CLI
    """)
    return


if __name__ == "__main__":
    app.run()
