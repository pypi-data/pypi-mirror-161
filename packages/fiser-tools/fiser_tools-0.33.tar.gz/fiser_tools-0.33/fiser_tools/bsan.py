#!/usr/bin/env python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def pareto_graph(variable, salida='tabla'):
    #Ordenar en descendente y pasar a dataframe
    pareto = variable.sort_values(ascending=False).to_frame()
    #Cambiar el nombre a la variable
    pareto.columns = ['Valor']
    #Crear la posición
    pareto['Posicion'] = np.arange(start=1, stop=len(pareto) + 1)
    pareto['Posicion_Porc'] = pareto.Posicion.transform(
        lambda x: x / pareto.shape[0] * 100)
    #Crear el acumulado
    pareto['Acum'] = pareto['Valor'].cumsum()
    max_pareto_acum = max(pareto.Acum)
    pareto['Acum_Porc'] = pareto.Acum.transform(
        lambda x: x / max_pareto_acum * 100)
    #Simplificar
    pareto = pareto[['Posicion_Porc', 'Acum_Porc']]

    value = 80
    idx = (pareto["Acum_Porc"] - value).abs().idxmin()
    idx2 = pareto["Acum_Porc"].idxmin()
    nearest = pareto["Posicion_Porc"].loc[idx]
    ini = pareto["Posicion_Porc"].loc[idx2]

    #Devolver la salida
    if salida == 'grafico':
        f, ax = plt.subplots(figsize=(10, 5))
        ax.plot(pareto.Posicion_Porc, pareto.Acum_Porc)
        ax.plot(pareto.Posicion_Porc, pareto.Posicion_Porc)
        ax.tick_params(axis='x', labelsize=12, labelrotation=90)
        ax.set_xticks(pareto.Posicion_Porc, pareto.index, rotation='vertical')
        ax.axvline(nearest, color='green', alpha=0.3)
        ax.text(nearest + 2, 0, "%.1f %%" % (nearest))
        ax.axhline(80, color='green', alpha=0.3, linestyle='dotted')
        ax.set_title("Pareto graph for '%s' by '%s'" %
                     (variable.name, variable.index.name))
        ax.fill_between([ini, nearest, nearest, ini], [0, 0, 100, 100],
                        alpha=0.3,
                        color='green')
        return (ax)
    else:
        return (pareto)


def clean_df_columns(df):
    for col in df.columns:
        new_col = col.lower()
        new_col = new_col.replace(" ", "_")
        new_col = new_col.replace("ó", "o")
        new_col = new_col.replace("í", "i").replace("á", "a").replace("é", "e")
        new_col = new_col.replace("ü", "u")
        new_col = new_col.replace("(", "")
        new_col = new_col.replace(")", "")
        new_col = new_col.replace("-", "")
        new_col = new_col.replace('º', "").replace("__", "_")
        new_col = new_col.replace("ñ", "n").replace("ú", "u").replace("í", "i")
        df.rename({col: new_col}, axis=1, inplace=True)
    return df
