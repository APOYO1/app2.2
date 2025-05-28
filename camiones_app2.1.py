import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean

# Cargar los datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("vehicle_positions.csv", sep=",")
    df = df.sort_values(by=["Vehiculo", "Tiempo"])
    return df

df = cargar_datos()

# Convertir columna de tiempo a datetime
df["Tiempo"] = pd.to_datetime(df["Tiempo"], format="%H:%M:%S")

# Selección de camión
camiones = df["Vehiculo"].unique()
vehiculo_seleccionado = st.selectbox("Selecciona un camión", camiones)
df_camion = df[df["Vehiculo"] == vehiculo_seleccionado].copy()

# Rango de tiempo para filtrar
hora_min = df_camion["Tiempo"].min()
hora_max = df_camion["Tiempo"].max()

col1, col2 = st.columns(2)
with col1:
    hora_inicio = st.time_input("Selecciona hora de inicio", hora_min.time())
with col2:
    hora_fin = st.time_input("Selecciona hora de fin", hora_max.time())

# Convertir a datetime para comparar
hora_inicio_dt = pd.to_datetime(hora_inicio.strftime("%H:%M:%S")).time()
hora_fin_dt = pd.to_datetime(hora_fin.strftime("%H:%M:%S")).time()

# Filtrar por hora
df_filtrado = df_camion[(df_camion["Tiempo"].dt.time >= hora_inicio_dt) & 
                        (df_camion["Tiempo"].dt.time <= hora_fin_dt)]

# Calcular distancia recorrida
distancia = 0
for i in range(1, len(df_filtrado)):
    p1 = (df_filtrado.iloc[i-1]["X"], -df_filtrado.iloc[i-1]["Z"])
    p2 = (df_filtrado.iloc[i]["X"], -df_filtrado.iloc[i]["Z"])
    distancia += euclidean(p1, p2)

# Calcular velocidad promedio solo con velocidades mayores a 0
velocidades_validas = df_filtrado[df_filtrado["Velocidad"] > 0]["Velocidad"]
velocidad_promedio = velocidades_validas.mean() if not velocidades_validas.empty else 0

# Mostrar resultados
st.markdown(f"**Distancia total recorrida:** {distancia:.2f} unidades")
st.markdown(f"**Velocidad promedio:** {velocidad_promedio:.2f} km/h")

# Gráfico 1: Ruta del camión
st.subheader("Ruta del camión")
fig1, ax1 = plt.subplots()
ax1.plot(df_filtrado["X"], -df_filtrado["Z"], marker='o', markersize=2, linestyle='-')
ax1.set_xlabel("X")
ax1.set_ylabel("Z (invertido)")
ax1.set_title("Ruta recorrida")
st.pyplot(fig1)

# Gráfico 2: Velocidad vs Tiempo
st.subheader("Velocidad a lo largo del tiempo")
fig2, ax2 = plt.subplots()
ax2.plot(df_filtrado["Tiempo"], df_filtrado["Velocidad"], color='green')
ax2.set_xlabel("Tiempo")
ax2.set_ylabel("Velocidad (km/h)")
ax2.set_title("Velocidad vs Tiempo")
st.pyplot(fig2)
