
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Listas más amplias
nombres = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
    "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"
]
apellidos = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"
]
combinaciones = random.sample([(n, a) for n in nombres for a in apellidos], 100)

# Inputs
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

        # Completar inputs
        driver.find_element(By.NAME, "firstName").clear()
        driver.find_element(By.NAME, "lastName").clear()
        driver.find_element(By.NAME, "city").clear()

        driver.find_element(By.NAME, "firstName").send_keys(nombre)
        driver.find_element(By.NAME, "lastName").send_keys(apellido)
        driver.find_element(By.NAME, "city").send_keys(ciudad)

        # Seleccionar estado
        state_select = driver.find_element(By.NAME, "state")
        for option in state_select.find_elements(By.TAG_NAME, "option"):
            if option.text.strip().lower() == estado.lower():
                option.click()
                break

        # Enviar formulario
        submit_btn = driver.find_element(By.CSS_SELECTOR, ".button-search[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_btn)

        # Esperar resultado
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "person")))
        person = driver.find_element(By.CLASS_NAME, "person")

        nombre_completo = person.find_element(By.CSS_SELECTOR, "#container-name h2").text.strip()
        edad = person.find_element(By.CSS_SELECTOR, ".flex h3").text.strip()

        # Teléfonos (Associated Phone Numbers y Last Known)
        telefonos = person.find_elements(By.CSS_SELECTOR, ".section-box ul.showMore-list li a[href*='/phone/']")
        telefonos_extraidos = list(set(t.text.strip() for t in telefonos if "(" in t.text))

        # Dirección
        try:
            direccion = person.find_element(By.XPATH, "//div[h3[text()='Last Known Address']]/div/p").text.strip().replace("\n", ", ")
        except:
            direccion = ""

        # Jobs
        try:
            jobs = person.find_elements(By.XPATH, "//div[h3[text()='Jobs']]/ul/li")
            trabajos = "; ".join(j.text.strip() for j in jobs)
        except:
            trabajos = ""

        # Education
        try:
            education = person.find_elements(By.XPATH, "//div[h3[text()='Education']]/ul/li")
            estudios = "; ".join(e.text.strip() for e in education)
        except:
            estudios = ""

        resultados.append({
            "Nombre": nombre_completo,
            "Edad": edad,
            "Teléfonos": "; ".join(telefonos_extraidos),
            "Dirección": direccion,
            "Empleos": trabajos,
            "Educación": estudios,
            "Ciudad": ciudad,
            "Estado": estado
        })
        print(f"✅ Guardado: {nombre_completo}")
    except Exception as e:
        print(f"❌ Error con {nombre} {apellido}: {str(e)}")
        continue

driver.quit()

# Guardar Excel
if resultados:
    df = pd.DataFrame(resultados)
    df.to_excel("personas_zabasearch.xlsx", index=False)
    print("🎯 Guardado en personas_zabasearch.xlsx")
else:
    print("⚠️ No se encontraron resultados válidos.")
