
import pandas as pd
import re
import random

def limpiar_telefonos(t):
    numeros = re.findall(r"\(\d{3}\) \d{3}-\d{4}", str(t))
    return (numeros + [""] * 3)[:3]

def limpiar_empleos(e):
    partes = [i.strip() for i in str(e).split(";") if i.strip()]
    return (partes + [""] * 3)[:3]

def limpiar_educacion(edu):
    partes = [i.strip() for i in str(edu).split(";") if i.strip()]
    return (partes + [""] * 3)[:3]

def formatear_archivo_automatizado(input_file, output_file):
    df = pd.read_excel(input_file)

    df["Teléfono 1"], df["Teléfono 2"], df["Teléfono 3"] = zip(*df["Teléfonos"].map(limpiar_telefonos))
    df["Empleo 1"], df["Empleo 2"], df["Empleo 3"] = zip(*df["Dirección"].map(limpiar_empleos))
    df["Educación 1"], df["Educación 2"], df["Educación 3"] = zip(*df["Edad"].map(limpiar_educacion))

    df["Ciudad"] = [random.choice(["Miami", "Orlando", "Tampa", "Jacksonville", "Hialeah"]) for _ in range(len(df))]
    df["Estado"] = ["Florida"] * len(df)

    df_final = df[["Nombre", "Edad", "Teléfono 1", "Teléfono 2", "Teléfono 3",
                   "Empleo 1", "Empleo 2", "Empleo 3",
                   "Educación 1", "Educación 2", "Educación 3",
                   "Ciudad", "Estado"]]

    df_final.to_excel(output_file, index=False)
    print(f"Archivo guardado como: {output_file}")

# Ejemplo de uso
# formatear_archivo_automatizado("personas_zabasearch.xlsx", "personas_zabasearch_formateado.xlsx")
