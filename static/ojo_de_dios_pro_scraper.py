import requests
import time
import csv

GOOGLE_API_KEY = "AIzaSyB3co_SwDrCoqJdbbJqWYyyOIz2EDxytLk"

rubros = [
    "tattoo artist", "barber", "makeup artist", "hair stylist", "personal trainer", "massage therapist",
    "real estate agent", "insurance broker", "auto detailer", "freelance photographer", "videographer",
    "handyman", "plumber", "electrician", "mobile mechanic", "DJ", "event planner", "private chef",
    "nail technician", "house cleaner", "painter", "landscaper", "roofer", "HVAC technician", "window cleaner",
    "dog walker", "personal chef", "carpenter", "gardener", "life coach", "financial advisor", "fitness coach",
    "nutritionist", "yoga instructor", "personal stylist", "eyelash technician", "graphic designer",
    "makeup studio", "drone operator", "wedding photographer", "wedding planner", "car audio installer",
    "eyebrow artist", "acupuncturist", "physical therapist"
]

ciudades = ["Miami, FL", "Fort Lauderdale, FL", "Hialeah, FL", "Hollywood, FL", "West Palm Beach, FL"]

def es_profesional_valido(nombre, telefono):
    excluidos = ["LLC", "Inc", "Corporation", "Group", "Team", "Center", "Company", "Firm", "Associates", "Office"]
    if not telefono or any(e.lower() in nombre.lower() for e in excluidos):
        return False
    if len(nombre.split()) > 5:
        return False
    if telefono.endswith("0000") or telefono.count("-") < 1:
        return False
    return True

def buscar_google_maps(query, ciudad, limite=20):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": f"{query} in {ciudad}", "key": GOOGLE_API_KEY}
    r = requests.get(url, params=params).json()
    leads = []
    for i, p in enumerate(r.get("results", [])):
        if i >= limite:
            break
        pid = p.get("place_id")
        if not pid:
            continue
        d_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={pid}&key={GOOGLE_API_KEY}"
        d = requests.get(d_url).json().get("result", {})
        nombre = d.get("name", "")
        tel = d.get("formatted_phone_number", "")
        dir = d.get("formatted_address", "")
        if es_profesional_valido(nombre, tel):
            leads.append([nombre, tel, dir, query, ciudad, "Google Maps"])
        time.sleep(0.1)  # más rápido pero sin sobrepasar límites
    return leads

def guardar_csv(leads, archivo):
    únicos = []
    vistos = set()
    for l in leads:
        if l[1] not in vistos:
            únicos.append(l)
            vistos.add(l[1])
    with open(archivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Nombre", "Teléfono", "Ubicación", "Rubro", "Ciudad", "Fuente"])
        writer.writerows(únicos)
    print(f"✅ Exportado: {archivo} con {len(únicos)} leads únicos.")

def ejecutar_busqueda():
    for ciudad in ciudades:
        leads_totales = []
        print(f"\n📍 Ciudad: {ciudad}")
        for rubro in rubros:
            print(f"   🔍 {rubro}")
            leads = buscar_google_maps(rubro, ciudad, limite=20)
            leads_totales.extend(leads)
        archivo_salida = f"leads_profesionales_{ciudad.replace(', ', '_').replace(' ', '_')}.csv"
        guardar_csv(leads_totales, archivo_salida)

if __name__ == "__main__":
    ejecutar_busqueda()
