import pandas as pd

# Cargar archivo original
df = pd.read_csv("leads_profesionales_Miami_FL.csv", delimiter=";")

# Lista de palabras que indican empresa o entidad
palabras_empresa = [
    "llc", "inc", "corp", "co.", "company", "group", "team", "center", "firm",
    "office", "solutions", "partners", "agency", "studio", "services", "spa",
    "salon", "clinic", "logistics", "media", "boutique"
]

# Función para filtrar solo personas físicas
def es_persona_fisica(nombre):
    nombre = str(nombre).lower()
    if any(palabra in nombre for palabra in palabras_empresa):
        return False
    if len(nombre.split()) <= 1:  # Solo un nombre suele ser negocio
        return False
    return True

# Filtrar
df_filtrado = df[df["Nombre"].apply(es_persona_fisica)]

# Guardar nuevo archivo limpio
df_filtrado.to_csv("leads_profesionales_Miami_FL_LIMPIO.csv", index=False, sep=";")
print(f"✅ Archivo limpio generado: leads_profesionales_Miami_FL_LIMPIO.csv ({len(df_filtrado)} filas)")
