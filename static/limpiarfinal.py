import pandas as pd
import random
import re

# Archivos
archivo_entrada = "leads_unificados_corregidos.csv"
archivo_salida = "leads_limpios_con_scoring.csv"

# Cargar datos
df = pd.read_csv(archivo_entrada, delimiter=";")

# Eliminar columnas innecesarias
df = df.drop(columns=["Ubicación", "Fuente"], errors="ignore")

# Formatear teléfonos: (954) 767-8833 → +19547678833
def formatear_telefono(tel):
    if pd.isna(tel):
        return ""
    solo_numeros = re.sub(r"\D", "", tel)
    if len(solo_numeros) == 10:
        return f"+1{solo_numeros}"
    elif len(solo_numeros) == 11 and solo_numeros.startswith("1"):
        return f"+{solo_numeros}"
    return tel  # si no cumple formato esperado

df["Teléfono"] = df["Teléfono"].apply(formatear_telefono)

# Agregar columna de Scoring aleatorio entre 600 y 850
df["Scoring"] = [random.randint(600, 850) for _ in range(len(df))]

# Exportar a nuevo archivo
df.to_csv(archivo_salida, index=False, sep=";")

print(f"✅ Archivo generado correctamente: {archivo_salida}")
