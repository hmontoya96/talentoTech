import os
import requests
from bs4 import BeautifulSoup

# URL de la página
URL = "https://www.epm.com.co/clientesyusuarios/energia/tarifas-energia/tarifas-anos-anteriores-energia.html#accordion-dc33e69ba6-item-d8ba3a3dea"

# Carpeta donde se guardarán los PDFs
OUTPUT_FOLDER = "pdfs_epm"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Obtener el contenido de la página
response = requests.get(URL)
soup = BeautifulSoup(response.content, "html.parser")

# Buscar todos los enlaces de los PDFs
documents = []
for accordion in soup.find_all("div", class_="cmp-accordion__item"):
    year_tag = accordion.find("span", class_="cmp-accordion__title")
    if year_tag:
        year = year_tag.text.strip()
        for card in accordion.find_all("div", class_="cmp-card-icon__text show"):
            month_tag = card.find("p")
            if month_tag:
                month_text = month_tag.text.strip()
                month_dict = {"Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04", "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08", "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"}
                month = month_dict.get(month_text, "")
                if month:
                    pdf_link = card.find_parent("a")
                    if pdf_link and "href" in pdf_link.attrs:
                        pdf_url = pdf_link["href"].strip()
                        if pdf_url.startswith("/"):
                            pdf_url = "https://www.epm.com.co" + pdf_url
                        file_name = f"{year}-{month}.pdf"
                        documents.append((file_name, pdf_url))

# Descargar los PDFs
for file_name, pdf_url in documents:
    pdf_path = os.path.join(OUTPUT_FOLDER, file_name)
    if not os.path.exists(pdf_path):
        print(f"Descargando {file_name}...")
        pdf_response = requests.get(pdf_url)
        with open(pdf_path, "wb") as f:
            f.write(pdf_response.content)
    else:
        print(f"{file_name} ya existe, omitiendo descarga.")

print("Descarga completada.")
