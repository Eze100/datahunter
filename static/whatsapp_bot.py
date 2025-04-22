import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Config
EXCEL_PATH = "static/empresas_unificadas.xlsx"
MENSAJE_PATH = "mensaje_temp.txt"
CHROMEDRIVER_PATH = "chromedriver.exe"

# Leer mensaje
if not os.path.exists(MENSAJE_PATH):
    print("❌ No se encontró mensaje_temp.txt")
    exit()

with open(MENSAJE_PATH, "r", encoding="utf-8") as f:
    mensaje = f.read().strip()

# Leer teléfonos
df = pd.read_excel(EXCEL_PATH)
df["Teléfono"] = df["Teléfono"].astype(str).str.replace(r"\D", "", regex=True)
telefonos = [t for t in df["Teléfono"] if t.startswith("54") and len(t) >= 10][:50]

# Navegador
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)
driver.get("https://web.whatsapp.com")
print("🕓 Escaneá el QR si no estás logueado...")
time.sleep(20)

# Probar con cada teléfono
for telefono in telefonos:
    try:
        print(f"🚀 Abriendo chat con {telefono}...")
        link = f"https://web.whatsapp.com/send?phone={telefono}&text={mensaje.replace(' ', '%20')}"
        driver.get(link)

        WebDriverWait(driver, 20).until_not(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label,'Iniciando chat')]"))
        )

        # Check error modal por número inválido
        modales_error = driver.find_elements(By.XPATH, "//div[contains(@aria-label,'no es válido')]")
        if modales_error:
            print(f"❌ Número inválido o sin WhatsApp: {telefono}")
            continue

        # Esperar input en el chat, no el buscador
        input_box = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//footer//div[@contenteditable='true'][@data-tab]"))
        )
        input_box.click()
        time.sleep(1)

        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//footer//button[@aria-label='Enviar']"))
        )
        send_button.click()

        print(f"✅ Mensaje enviado a {telefono}")
        time.sleep(5)

    except Exception as e:
        print(f"🔥 Error con {telefono}: {e}")
        continue

driver.quit()
