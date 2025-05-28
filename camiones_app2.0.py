import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
import datetime

# Cargar los datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("vehicle_positions.csv", sep=",")
    df = df.sort_values(by=["Vehiculo", "Tiempo"])
    return df

df = cargar_datos()

# Selección de camión
camiones = df["Vehiculo"].unique()
vehiculo_seleccionado = st.selectbox("Selecciona un camión", camiones)

df_camion = df[df["Vehiculo"] == vehiculo_seleccionado].copy()

# Convertir columna "Tiempo" a datetime
df_camion["Tiempo"] = pd.to_datetime(df_camion["Tiempo"], format="%H:%M:%S").dt.time

# Sidebar: selección de hora de inicio y fin
st.sidebar.markdown("### Selección de intervalo de tiempo")
hora_inicio = st.sidebar.time_input("Hora de inicio", value=datetime.time(16, 53, 36))
hora_fin = st.sidebar.time_input("Hora de fin", value=datetime.time(17, 10, 0))

# Filtrar el DataFrame por el intervalo de tiempo
df_camion = df_camion[(df_camion["Tiempo"] >= hora_inicio) & (df_camion["Tiempo"] <= hora_fin)]

# Volver a convertir Tiempo a datetime para graficar (agrega una fecha cualquiera)
df_camion["Tiempo"] = pd.to_datetime(df_camion["Tiempo"].astype(str))

# Calcular métricas
distancia = 0
for i in range(1, len(df_camion)):
    p1 = (df_camion.iloc[i-1]["X"], -df_camion.iloc[i-1]["Z"])
    p2 = (df_camion.iloc[i]["X"], -df_camion.iloc[i]["Z"])
    distancia += euclidean(p1, p2)

# Velocidad promedio
tiempo_total = (df_camion["Tiempo"].iloc[-1] - df_camion["Tiempo"].iloc[0]).total_seconds() / 3600  # en horas
velocidad_promedio = distancia / tiempo_total if tiempo_total > 0 else 0

# Mostrar métricas
st.metric("Distancia total (m)", f"{distancia:.2f}")
st.metric("Velocidad promedio (m/h)", f"{velocidad_promedio:.2f}")

# Graficar recorrido
fig, ax = plt.subplots()
ax.plot(df_camion["X"], -df_camion["Z"], marker="o")
ax.set_title(f"Recorrido del camión {vehiculo_seleccionado}")
ax.set_xlabel("X")
ax.set_ylabel("Z (invertido)")
st.pyplot(fig)
