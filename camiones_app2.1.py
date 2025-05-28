import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean

# Cargar los datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("vehicle_positions.csv", sep=",")
    df = df.sort_values(by=["Vehiculo", "Tiempo"])
    df["Tiempo"] = pd.to_datetime(df["Tiempo"], format="%H:%M:%S")
    return df

df = cargar_datos()

# Filtro por rango de hora
hora_min = df["Tiempo"].dt.time.min()
hora_max = df["Tiempo"].dt.time.max()
rango_hora = st.slider("Selecciona el rango de tiempo", value=(hora_min, hora_max))
df = df[(df["Tiempo"].dt.time >= rango_hora[0]) & (df["Tiempo"].dt.time <= rango_hora[1])]

# Calcular duración por vehículo y filtrar por tiempo mínimo de actividad
minutos_minimos = st.number_input("Filtrar camiones con menos de X minutos de actividad", value=15)
vehiculos_filtrados = []
for veh in df["Vehiculo"].unique():
    tiempos = df[df["Vehiculo"] == veh]["Tiempo"]
    if (tiempos.max() - tiempos.min()).total_seconds() / 60 >= minutos_minimos:
        vehiculos_filtrados.append(veh)

if not vehiculos_filtrados:
    st.warning("No hay camiones que cumplan con el mínimo de minutos seleccionados.")
    st.stop()

# Selección de camión
vehiculo_seleccionado = st.selectbox("Selecciona un camión", vehiculos_filtrados)
df_camion = df[df["Vehiculo"] == vehiculo_seleccionado].copy()

# Calcular velocidades y distancias
velocidades = [0]
distancias = [0]
distancia_total = 0
for i in range(1, len(df_camion)):
    p1 = (df_camion.iloc[i-1]["X"], -df_camion.iloc[i-1]["Z"])
    p2 = (df_camion.iloc[i]["X"], -df_camion.iloc[i]["Z"])
    d = euclidean(p1, p2)
    distancia_total += d
    distancias.append(d)
    delta_t = (df_camion.iloc[i]["Tiempo"] - df_camion.iloc[i-1]["Tiempo"]).total_seconds()
    v = (d / delta_t) if delta_t > 0 else 0
    velocidades.append(v)

df_camion["Distancia"] = distancias

# Calcular velocidad en km/h
df_camion["Velocidad_m_s"] = velocidades

# Opción para el cálculo de velocidad promedio
opcion_velocidad = st.radio("¿Cómo deseas calcular la velocidad promedio?", [
    "Tiempo total",
    "Solo tiempo en movimiento"
])

tiempo_total = (df_camion["Tiempo"].iloc[-1] - df_camion["Tiempo"].iloc[0]).total_seconds()
if opcion_velocidad == "Tiempo total":
    velocidad_prom_kmh = (distancia_total / tiempo_total) * 3.6
else:
    tiempo_mov = df_camion[df_camion["Velocidad_m_s"] > 0]["Tiempo"].diff().dt.total_seconds().sum()
    velocidad_prom_kmh = (distancia_total / tiempo_mov) * 3.6 if tiempo_mov else 0

velocidad_max_kmh = max(velocidades) * 3.6

# Métricas
st.metric("Distancia total (m)", f"{distancia_total:.2f}")
st.metric("Velocidad promedio (km/h)", f"{velocidad_prom_kmh:.2f}")
st.metric("Velocidad máxima (km/h)", f"{velocidad_max_kmh:.2f}")

# Gráfico 1: Recorrido individual en planta
fig1, ax1 = plt.subplots()
ax1.plot(df_camion["X"], -df_camion["Z"], marker='o')
ax1.set_title("Recorrido del camión seleccionado")
ax1.set_xlabel("X")
ax1.set_ylabel("-Z")
st.pyplot(fig1)

# Gráfico 2: Recorrido conjunto de todos los camiones
fig2, ax2 = plt.subplots()
for veh in vehiculos_filtrados:
    df_v = df[df["Vehiculo"] == veh]
    ax2.plot(df_v["X"], -df_v["Z"], label=f"{veh}")
ax2.set_title("Recorridos en conjunto")
ax2.set_xlabel("X")
ax2.set_ylabel("-Z")
ax2.legend()
st.pyplot(fig2)

# Gráfico 3: Evolución del llenado (distancia acumulada vs tiempo)
df_camion["Distancia_acumulada"] = df_camion["Distancia"].cumsum()
fig3, ax3 = plt.subplots()
ax3.plot(df_camion["Tiempo"], df_camion["Distancia_acumulada"])
ax3.set_title("Evolución del llenado (Distancia acumulada)")
ax3.set_xlabel("Tiempo")
ax3.set_ylabel("Distancia acumulada (m)")
st.pyplot(fig3)

# Distancia total conjunta de todos los camiones
distancia_conjunta = 0
for veh in vehiculos_filtrados:
    df_v = df[df["Vehiculo"] == veh]
    for i in range(1, len(df_v)):
        p1 = (df_v.iloc[i-1]["X"], -df_v.iloc[i-1]["Z"])
        p2 = (df_v.iloc[i]["X"], -df_v.iloc[i]["Z"])
        distancia_conjunta += euclidean(p1, p2)

st.metric("Distancia total recorrida por todos los camiones (m)", f"{distancia_conjunta:.2f}")
