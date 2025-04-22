import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Listas para prueba rápida (ampliar después)
nombres = ["James", "Mary", "John", "Patricia", "Robert"]
apellidos = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
combinaciones = random.sample([(n, a) for n in nombres for a in apellidos], 25)

# Input
ciudad = input("Ingrese ciudad (ej: Miami): ").strip()
estado = input("Ingrese estado (ej: Florida): ").strip()

# Setup navegador
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0")
driver = webdriver.Chrome(options=options)

resultados = []

for idx, (nombre, apellido) in enumerate(combinaciones):
    print(f"🔍 [{idx+1}] {nombre} {apellido} - {ciudad}, {estado}")
    try:
        driver.get("https://www.zabasearch.com/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "firstName")))

        # Completar campos
        first_input = driver.find_element(By.NAME, "firstName")
        last_input = driver.find_element(By.NAME, "lastName")
        city_input = driver.find_element(By.NAME, "city")
        state_select = driver.find_element(By.NAME, "state")

        first_input.clear(); time.sleep(0.2)
        first_input.send_keys(nombre); time.sleep(0.2)

        last_input.clear(); time.sleep(0.2)
        last_input.send_keys(apellido); time.sleep(0.2)

        city_input.clear(); time.sleep(0.2)
        city_input.send_keys(ciudad); time.sleep(0.2)

        # Seleccionar estado
        for option in state_select.find_elements(By.TAG_NAME, "option"):
            if option.text.strip().lower() == estado.lower():
                option.click(); break
        time.sleep(0.5)

        # Botón de búsqueda con JS
        submit_btn = driver.find_element(By.CSS_SELECTOR, ".button-search[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_btn)

        # Esperar resultados
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "person")))
        person = driver.find_element(By.CLASS_NAME, "person")

        nombre_completo = person.find_element(By.CSS_SELECTOR, "#container-name h2").text.strip()
        edad = person.find_element(By.CSS_SELECTOR, ".flex h3").text.strip()
        telefonos = person.find_elements(By.CSS_SELECTOR, "div.section-box h4")
        telefonos_extraidos = [t.text.strip() for t in telefonos if t.text.strip().startswith("(")]

        try:
            direccion = person.find_element(By.XPATH, "//div[h3[text()='Last Known Address']]/div/p").text.strip().replace("\\n", ", ")
        except:
            direccion = ""

        resultados.append({
            "Nombre": nombre_completo,
            "Edad": edad,
            "Teléfonos": "; ".join(telefonos_extraidos),
            "Dirección": direccion,
            "Ciudad": ciudad,
            "Estado": estado
        })
        print(f"✅ Guardado: {nombre_completo}")
    except Exception as e:
        print(f"❌ Error con {nombre} {apellido}: {str(e)}")
        continue

driver.quit()

# Guardar resultados
if resultados:
    df = pd.DataFrame(resultados)
    df.to_excel("personas_zabasearch.xlsx", index=False)
    print("🎯 Guardado en personas_zabasearch.xlsx")
else:
    print("⚠️ No se encontraron resultados válidos.")
