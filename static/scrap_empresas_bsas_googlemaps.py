import requests
import time
import pandas as pd
import sys
import os

API_KEY = "AIzaSyB3co_SwDrCoqJdbbJqWYyyOIz2EDxytLk"

if len(sys.argv) < 3:
    print("Faltan argumentos: zona y rubro")
    sys.exit(1)

zona = sys.argv[1]
rubro = sys.argv[2]

def buscar_google_maps(query, localidad, max_results=50):
    url_base = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    detalles_url = "https://maps.googleapis.com/maps/api/place/details/json"
    headers = {"Accept": "application/json"}
    leads = []

    full_query = f"{query} en {localidad}, Buenos Aires, Argentina"
    params = {"query": full_query, "key": API_KEY}
    res = requests.get(url_base, headers=headers, params=params).json()

    for result in res.get("results", [])[:max_results]:
        nombre = result.get("name", "")
        direccion = result.get("formatted_address", "")
        place_id = result.get("place_id")

        telefono = ""
        web = ""
        correo = ""

        if place_id:
            try:
                d_params = {
                    "place_id": place_id,
                    "key": API_KEY,
                    "fields": "name,formatted_address,international_phone_number,website,url"
                }
                detalles = requests.get(detalles_url, headers=headers, params=d_params).json().get("result", {})

                telefono = detalles.get("international_phone_number", "")
                web = detalles.get("website", "")
                direccion = detalles.get("formatted_address", direccion)

            except Exception as e:
                print(f"Error obteniendo detalles: {e}")

        leads.append({
            "Nombre": nombre,
            "Teléfono": telefono,
            "Dirección": direccion,
            "Web": web,
            "Correo": correo,
            "Rubro": query,
            "Zona": localidad
        })
        time.sleep(0.4)

    return leads

print(f"Buscando '{rubro}' en {zona}...")
datos = buscar_google_maps(rubro, zona)

# Crear carpeta output si no existe
os.makedirs("output", exist_ok=True)

# Formatear nombre del archivo: rubro_zona.xlsx
nombre_archivo = f"{rubro.strip().lower().replace(' ', '_')}_{zona.strip().lower().replace(' ', '_')}.xlsx"
output_path = f"output/{nombre_archivo}"

df = pd.DataFrame(datos)
df.to_excel(output_path, index=False)
print(f"Archivo guardado en: {output_path}")
