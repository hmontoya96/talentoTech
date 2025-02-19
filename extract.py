import re
import pandas as pd
import PyPDF2

def extract_text_from_pdf(pdf_path):
    """Extrae el texto de todas las páginas del PDF."""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_data(text):
    """Extrae los datos específicos de tarifas utilizando expresiones regulares."""
    data = []
    
    patterns = [
        (r"Estrato 1\. Rango 0 - CS\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa Residencial", "Estrato 1", "Rango 0 - CS"),
        (r"Estrato 1\. Rango > CS\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa Residencial", "Estrato 1", "Rango > CS"),
        (r"Estrato 2\. Rango 0 - CS\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa Residencial", "Estrato 2", "Rango 0 - CS"),
        (r"Estrato 2\. Rango > CS\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa Residencial", "Estrato 2", "Rango > CS"),
        (r"Estrato 3\. Rango 0 - CS\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa Residencial", "Estrato 3", "Rango 0 - CS"),
        (r"Estrato 3\. Rango > CS\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa Residencial", "Estrato 3", "Rango > CS"),
        (r"Estrato 4\. Todo el consumo\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa Residencial", "Estrato 4", "Todo el consumo"),
        (r"Estrato 5 y 6\. Todo el consumo\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa Residencial", "Estrato 5 y 6", "Todo el consumo"),
        (r"Industrial y Comercial\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa No Residencial", "Industrial y Comercial", "Valor único"),
        (r"ESPD\*\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa No Residencial", "ESPD*", "Valor único"),
        (r"Oficial y Exentos de Contribución\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa No Residencial", "Oficial y Exentos de Contribución", "Valor único"),
        (r"Industrial y Comercial\s+Punta\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa Horaria No Residencial", "Industrial y Comercial", "Punta"),
        (r"Industrial y Comercial\s+Fuera de Punta\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa Horaria No Residencial", "Industrial y Comercial", "Fuera de Punta"),
        (r"Oficial y Exentos\s+Punta\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa Horaria No Residencial", "Oficial y Exentos", "Punta"),
        (r"Oficial y Exentos\s+Fuera de Punta\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", "Tarifa Horaria No Residencial", "Oficial y Exentos", "Fuera de Punta")
    ]
    
    for pattern, section, subsection, category in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            data.append([section, subsection, category, float(match[0]), float(match[1]), float(match[2])])
    
    return pd.DataFrame(data, columns=["Sección", "Subsección", "Tipo", "Propiedad EPM", "Propiedad Compartido", "Propiedad Cliente"])

def main():
    try:
        pdf_path = '2024-12.pdf'
        pdf_text = extract_text_from_pdf(pdf_path)
        df = extract_data(pdf_text)
        df.to_csv('tarifas_extraidas.csv', index=False, encoding='utf-8-sig')
        print("Datos exportados exitosamente a tarifas_extraidas.csv")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()