import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Diseño Marshall", layout="wide")
st.title("Aplicación de Diseño de Mezclas Asfálticas - Método Marshall")

st.header("1. Datos de Entrada")

with st.expander("Configuración de Materiales"):
    Gsb = st.number_input("Gravedad Específica Bulk de Agregados (Gsb)", value=2.703)
    Gmm = st.number_input("Gravedad Específica Teórica Máxima (Gmm)", value=2.454)
    Gse = st.number_input("Gravedad Específica Efectiva (Gse)", value=2.730)
    Gsa = st.number_input("Gravedad Específica Aparente (Gsa)", value=2.758)

st.subheader("2. Datos de Especímenes")
st.markdown("Ingrese los datos para cada contenido de asfalto")

columns = [
    "% Asfalto", "Peso Aire (g)", "Peso Sumergido (g)", "Peso Saturado Superficial Seco (g)",
    "Estabilidad (lbs)", "Flujo (0.01\")"
]

def empty_row():
    return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

num_rows = st.number_input("Cantidad de especímenes", min_value=1, max_value=20, value=10)
data = pd.DataFrame([empty_row() for _ in range(num_rows)], columns=columns)
data = st.data_editor(data, num_rows="dynamic", key="specimen_data")

# Calculos
if st.button("Calcular y Graficar"):
    data["Gmb"] = data["Peso Aire (g)"] / (data["Peso Saturado Superficial Seco (g)"] - data["Peso Sumergido (g)"])
    data["VTM (%)"] = (1 - (data["Gmb"] / Gmm)) * 100
    data["VMA (%)"] = 100 - ((data["Gmb"] * (100 - data["% Asfalto"]) / 100) / Gsb)
    data["VFA (%)"] = ((data["VMA (%)"] - data["VTM (%)"]) / data["VMA (%)"]) * 100

    st.subheader("Resultados Calculados")
    st.dataframe(data.round(2))

    st.subheader("Gráficas")
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].plot(data["% Asfalto"], data["Estabilidad (lbs)"], marker='o')
    axes[0, 0].set_title("Estabilidad vs % Asfalto")
    axes[0, 0].set_ylabel("Estabilidad (lbs)")

    axes[0, 1].plot(data["% Asfalto"], data["Flujo (0.01\")"], marker='o')
    axes[0, 1].set_title("Flujo vs % Asfalto")
    axes[0, 1].set_ylabel("Flujo")

    axes[0, 2].plot(data["% Asfalto"], data["VTM (%)"], marker='o')
    axes[0, 2].set_title("VTM vs % Asfalto")

    axes[1, 0].plot(data["% Asfalto"], data["VMA (%)"], marker='o')
    axes[1, 0].set_title("VMA vs % Asfalto")

    axes[1, 1].plot(data["% Asfalto"], data["VFA (%)"], marker='o')
    axes[1, 1].set_title("VFA vs % Asfalto")

    axes[1, 2].plot(data["% Asfalto"], data["Gmb"], marker='o')
    axes[1, 2].set_title("Densidad Bulk (Gmb) vs % Asfalto")

    for ax in axes.flat:
        ax.grid(True)
        ax.set_xlabel("% Asfalto")

    st.pyplot(fig)

    st.subheader("Contenido Óptimo de Asfalto (Método NAPA)")
    target_vtm = 4.0
    closest_row = data.iloc[(data["VTM (%)"] - target_vtm).abs().argsort()[:1]]
    st.write("Contenido de asfalto con VTM ≤ 4%:")
    st.dataframe(closest_row)

# Granulometría
st.header("3. Análisis de Granulometría")
st.markdown("Ingrese los porcentajes que pasan para cada tamiz por agregado.")

tamices = ["1 1/2\"", "3/8\"", "N°4", "N°8", "N°16", "N°30", "N°50", "N°100", "N°200"]
agg_cols = ["Agregado 1", "Agregado 2", "Agregado 3", "Agregado 4"]
mezcla_cols = ["% Mezcla 1", "% Mezcla 2", "% Mezcla 3", "% Mezcla 4"]

# Entrada granulometría
granulo = pd.DataFrame(index=tamices, columns=agg_cols)
granulo = st.data_editor(granulo.astype(float), num_rows="fixed", key="granulo")

st.markdown("Ingrese los porcentajes de mezcla para cada agregado (deben sumar 1.0):")
pmezcla = [st.number_input(col, min_value=0.0, max_value=1.0, step=0.01, value=0.25, key=f"mezcla_{i}") for i, col in enumerate(mezcla_cols)]

if sum(pmezcla) != 1.0:
    st.warning("⚠️ La suma de los porcentajes de mezcla debe ser 1.0")

# Calcular combinación
if st.button("Calcular combinación granulométrica"):
    matriz = granulo.values.astype(float)
    combinacion = np.dot(matriz, pmezcla)
    df_result = pd.DataFrame({"Tamiz": tamices, "Combinación Resultante (%)": combinacion})

    st.subheader("Combinación Resultante")
    st.dataframe(df_result.set_index("Tamiz"))

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    for i, col in enumerate(agg_cols):
        ax2.plot(tamices, granulo[col], label=col, linestyle="--")
    ax2.plot(tamices, combinacion, label="Combinación", linewidth=2, color="black")
    ax2.set_title("Curva Granulométrica")
    ax2.set_ylabel("% que pasa")
    ax2.set_xlabel("Tamiz")
    ax2.invert_xaxis()
    ax2.grid(True)
    ax2.legend()
    st.pyplot(fig2)
