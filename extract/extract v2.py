import pdfplumber
import re
import csv
import os

# Ruta del archivo PDF
pdf_path = "2024-12.pdf"

# Expresión regular optimizada para capturar los valores completos de cada categoría
expresiones = {
    "Industrial y Comercial": r"Industrial y Comercial\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Oficial y Exentos": r"Oficial y Exentos\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)"
}

# Lista para almacenar los datos extraídos
datos_extraidos = []

# Leer el PDF y buscar los datos
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        texto = page.extract_text()
        if texto:
            for categoria, patron in expresiones.items():
                match = re.search(patron, texto)
                if match:
                    datos_extraidos.append([categoria] + list(match.groups()))

# Ruta del archivo CSV
csv_path = "tarifasss_extraidas.csv"

# Verificar si el archivo ya existe
archivo_existe = os.path.exists(csv_path)

# Guardar en CSV sin sobrescribir datos previos
with open(csv_path, mode="a", newline="", encoding="utf-8") as archivo_csv:
    escritor = csv.writer(archivo_csv)
    # Escribir encabezado solo si el archivo es nuevo
    if not archivo_existe:
        escritor.writerow(["Categoría", 
                           "Nivel II - Punta", "Nivel II - Fuera de Punta", 
                           "Nivel III - Punta", "Nivel III - Fuera de Punta", 
                           "Nivel IV - Punta", "Nivel IV - Fuera de Punta"])
    # Escribir nuevos datos
    escritor.writerows(datos_extraidos)
