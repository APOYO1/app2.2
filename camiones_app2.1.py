import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean

# Cargar los datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("vehicle_positions.csv", sep=",")
    df = df.sort_values(by=["Vehiculo", "Tiempo"])
    df["Tiempo"] = pd.to_datetime(df["Tiempo"])
    return df

df = cargar_datos()

# Selección de camión
camiones = df["Vehiculo"].unique()
vehiculo_seleccionado = st.selectbox("Selecciona un camión", camiones)

# Filtrar por camión
df_camion = df[df["Vehiculo"] == vehiculo_seleccionado].copy()

# Rango de horas disponibles
hora_min = df_camion["Tiempo"].min().time()
hora_max = df_camion["Tiempo"].max().time()

st.write("Selecciona el rango horario del ejercicio:")
col1, col2 = st.columns(2)
with col1:
    hora_inicio = st.time_input("Hora de inicio", value=hora_min)
with col2:
    hora_fin = st.time_input("Hora de fin", value=hora_max)

# Convertir a datetime para filtrar
fecha_base = df_camion["Tiempo"].dt.date.iloc[0]
inicio_dt = pd.to_datetime(f"{fecha_base} {hora_inicio}")
fin_dt = pd.to_datetime(f"{fecha_base} {hora_fin}")

df_filtrado = df_camion[(df_camion["Tiempo"] >= inicio_dt) & (df_camion["Tiempo"] <= fin_dt)]

# Calcular métricas con los datos filtrados
distancia = 0
for i in range(1, len(df_filtrado)):
    p1 = (df_filtrado.iloc[i-1]["X"], -df_filtrado.iloc[i-1]["Z"])
    p2 = (df_filtrado.iloc[i]["X"], -df_filtrado.iloc[i]["Z"])
    distancia += euclidean(p1, p2)

velocidad_promedio = df_filtrado["Velocidad"].mean()

# Mostrar métricas
st.metric("Distancia recorrida (aprox.)", f"{distancia:.2f} m")
st.metric("Velocidad promedio", f"{velocidad_promedio:.2f} km/h")

# Mostrar trayectoria
fig, ax = plt.subplots()
ax.plot(df_filtrado["X"], -df_filtrado["Z"], marker="o", linestyle="-")
ax.set_title(f"Ruta del camión {vehiculo_seleccionado}")
ax.set_xlabel("X")
ax.set_ylabel("Z (invertido)")
st.pyplot(fig)
