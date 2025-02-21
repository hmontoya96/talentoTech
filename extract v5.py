import pdfplumber
import re
import csv

# Ruta del archivo PDF
pdf_path = "unificado.pdf"

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

# Expresión regular para extraer el período
regex_periodo = r"(?:Tarifas y Costo de Energía Eléctrica.*?-\s*)\s*(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)\s*de\s*(\d{4})"

# Diccionario para conversión de meses
meses = {
    "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
    "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
    "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"
}

# Listas para almacenar los datos extraídos
datos_extraidos1 = []
datos_extraidos2 = []

# Leer el PDF y extraer datos
with pdfplumber.open(pdf_path) as pdf:
    periodo_actual = None  # Variable para almacenar el período por página

    for page in pdf.pages:
        texto = page.extract_text()
        if texto:
            # Buscar el período en cada página
            match_periodo = re.search(regex_periodo, texto, re.IGNORECASE)
            if match_periodo:
                mes_texto, anio = match_periodo.groups()
                periodo_actual = anio + meses[mes_texto.capitalize()]  # Convertir a formato YYYYMM
            
            # Si no se encuentra el período en la página, usar el último detectado
            if not periodo_actual:
                continue  # Si aún no tenemos un período válido, omitir la página

            # Extraer datos de expresiones1
            for categoria, patron in expresiones1.items():
                match = re.search(patron, texto)
                if match:
                    datos_extraidos1.append([categoria] + list(match.groups()) + [periodo_actual])

            # Extraer datos de expresiones2
            for categoria, patron in expresiones2.items():
                match = re.search(patron, texto)
                if match:
                    datos_extraidos2.append([categoria] + list(match.groups()) + [periodo_actual])

# Ruta de los archivos CSV
csv_path1 = "tarifas_estratos.csv"
csv_path2 = "tarifas_industriales.csv"

# Guardar datos del primer conjunto en CSV
with open(csv_path1, mode="w", newline="", encoding="utf-8") as archivo_csv:
    escritor = csv.writer(archivo_csv)
    escritor.writerow(["Categoría", "Propiedad EPM", "Propiedad Compartido", "Propiedad Cliente", "Periodo"])
    escritor.writerows(datos_extraidos1)

# Guardar datos del segundo conjunto en CSV
with open(csv_path2, mode="w", newline="", encoding="utf-8") as archivo_csv:
    escritor = csv.writer(archivo_csv)
    escritor.writerow(["Categoría", "Nivel II - Punta", "Nivel II - Fuera de Punta", "Nivel III - Punta", "Nivel III - Fuera de Punta", "Nivel IV - Punta", "Nivel IV - Fuera de Punta", "Periodo"])
    escritor.writerows(datos_extraidos2)

print("Archivos CSV generados con éxito.")
