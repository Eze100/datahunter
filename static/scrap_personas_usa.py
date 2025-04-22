import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Combinaciones base
nombres = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth"]
apellidos = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
combinaciones = random.sample([(n, a) for n in nombres for a in apellidos], 100)

# Input
ciudad = input("Ingrese la ciudad y estado (ej: Miami, FL): ").strip()

# Setup Selenium
options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
options.add_argument(f"user-agent={user_agent}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")
options.add_argument("--headless")  # sacá esto para test visual
driver = webdriver.Chrome(options=options)

resultados = []

for idx, (nombre, apellido) in enumerate(combinaciones):
    print(f"🔎 [{idx+1}] Buscando: {nombre} {apellido} en {ciudad}")
    try:
        driver.get("https://peoplesearch.com/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name-input")))

        name_input = driver.find_element(By.ID, "name-input")
        location_input = driver.find_element(By.ID, "location-input")

        name_input.clear()
        location_input.clear()
        time.sleep(0.5)

        name_input.send_keys(f"{nombre} {apellido}")
        location_input.send_keys(ciudad)
        location_input.send_keys(Keys.RETURN)

        try:
            link = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/person/']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", link)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", link)
        except:
            print("⚠️ No se encontraron resultados.")
            continue

        # Detalles del perfil
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "name-location-heading")))
        nombre_completo = driver.find_element(By.ID, "name-location-heading").text.split("\n")[0].strip()
        edad = driver.find_element(By.ID, "aprox-age-heading").text.strip()

        try:
            telefono = driver.find_element(By.ID, "landline-0").text.strip()
        except:
            telefono = ""

        try:
            dir1 = driver.find_element(By.ID, "current-address-line-1").text.strip()
            dir2 = driver.find_element(By.ID, "current-address-line-2").text.strip()
            direccion = f"{dir1}, {dir2}"
        except:
            direccion = ""

        try:
            otras_direcciones = "; ".join([
                d.text.strip() for d in driver.find_elements(By.CSS_SELECTOR, "div[id^='other-locations-']")
            ])
        except:
            otras_direcciones = ""

        try:
            relacionados = "; ".join([
                f.text.strip() for f in driver.find_elements(By.CSS_SELECTOR, "div[id^='relatives-'] a")
            ])
        except:
            relacionados = ""

        resultados.append({
            "Nombre": nombre_completo,
            "Edad": edad,
            "Teléfono": telefono,
            "Dirección Principal": direccion,
            "Otras Direcciones": otras_direcciones,
            "Relacionados": relacionados,
            "Ciudad": ciudad
        })

        print(f"✅ Guardado: {nombre_completo}")

    except Exception as e:
        print(f"❌ Error con {nombre} {apellido}: {e}")

# Exportar
if resultados:
    df = pd.DataFrame(resultados)
    df.to_excel("personas_usa.xlsx", index=False)
    print("🎯 Archivo guardado como personas_usa.xlsx")
else:
    print("⚠️ No se encontraron resultados válidos.")

driver.quit()
