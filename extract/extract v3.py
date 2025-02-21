import pdfplumber
import re
import csv
import os

# Ruta del archivo PDF
pdf_path = "2024-12.pdf"

# Expresiones regulares para cada registro
expresiones1 = {
    "Estrato 1 - Rango 0 - CS": r"Estrato 1\.\s*Rango 0 - CS\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Estrato 1 - Rango > CS": r"\s*Rango > CS\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Estrato 2 - Rango 0 - CS": r"Estrato 2\.\s*Rango 0 - CS\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Estrato 2 - Rango > CS": r"\s*Rango > CS\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Estrato 3 - Rango 0 - CS": r"Estrato 3\.\s*Rango 0 - CS\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Estrato 3 - Rango > CS": r"\s*Rango > CS\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Estrato 4 - Todo el consumo": r"Estrato 4\.\s*Todo el consumo\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Estrato 5 y 6 - Todo el consumo": r"Estrato 5 y 6\.\s*Todo el consumo\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Industrial y Comercial": r"Industrial y Comercial\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "ESPD*": r"ESPD\*\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Oficial y Exentos de Contribución": r"Oficial y Exentos de Contribución\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Industrial y Comercial - Punta": r"Industrial y\s+Punta\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Industrial y Comercial - Fuera de Punta": r"Comercial\s+Fuera de Punta\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Oficial y Exentos - Punta": r"Oficial y\s+Punta\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Oficial y Exentos - Fuera de Punta": r"Exentos\s+Fuera de Punta\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)"
}

expresiones2 = {
    "Industrial y Comercial": r"Industrial y Comercial\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
    "Oficial y Exentos": r"Oficial y Exentos\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)"
}

# Lista para almacenar los datos extraídos
datos_extraidos1 = []
datos_extraidos2 = []

# Leer el PDF
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        texto = page.extract_text()
        if texto:
            for categoria, patron in expresiones1.items():
                match = re.search(patron, texto)
                if match:
                    datos_extraidos1.append([categoria] + list(match.groups()))
            for categoria, patron in expresiones2.items():
                match = re.search(patron, texto)
                if match:
                    datos_extraidos2.append([categoria] + list(match.groups()))

# Ruta del archivo CSV
csv_path1 = "tarifas_estratos.csv"
csv_path2 = "tarifas_industriales.csv"

# Guardar datos del primer conjunto en CSV
with open(csv_path1, mode="w", newline="", encoding="utf-8") as archivo_csv:
    escritor = csv.writer(archivo_csv)
    escritor.writerow(["Categoría", "Propiedad EPM", "Propiedad Compartido", "Propiedad Cliente"])
    escritor.writerows(datos_extraidos1)

# Guardar datos del segundo conjunto en CSV
with open(csv_path2, mode="w", newline="", encoding="utf-8") as archivo_csv:
    escritor = csv.writer(archivo_csv)
    escritor.writerow(["Categoría", "Nivel II - Punta", "Nivel II - Fuera de Punta", "Nivel III - Punta", "Nivel III - Fuera de Punta", "Nivel IV - Punta", "Nivel IV - Fuera de Punta"])
    escritor.writerows(datos_extraidos2)
