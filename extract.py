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
    data = []
    
    # Definir las secciones principales
    sections = {
        'Tarifa Residencial': {
            'pattern': r'Tarifa Residencial(.*?)Tarifa No Residencial',
            'subsections': [
                {'name': 'Estrato 1', 'type': 'estrato'},
                {'name': 'Estrato 2', 'type': 'estrato'},
                {'name': 'Estrato 3', 'type': 'estrato'},
                {'name': 'Estrato 4', 'type': 'consumo'},
                {'name': 'Estrato 5 y 6', 'type': 'consumo'}
            ]
        },
        'Tarifa No Residencial': {
            'pattern': r'Tarifa No Residencial(.*?)Tarifa Áreas Comunes',
            'items': [
                'Industrial y Comercial',
                'ESPD\*',
                'Oficial y Exentos de Contribución'
            ]
        },
        'Tarifa Áreas Comunes': {
            'pattern': r'Tarifa Áreas Comunes(.*?)$',
            'items': [
                'Con contribución',
                'Sin contribución'
            ]
        }
    }

    def extract_values(line):
        """Extrae los valores numéricos de una línea."""
        values = re.findall(r'\d+\.\d+', line)
        if len(values) >= 3:
            return [float(values[0]), float(values[1]), float(values[2])]
        return None

    for section_name, section_info in sections.items():
        # Extraer la sección completa
        section_match = re.search(section_info['pattern'], text, re.DOTALL)
        if section_match:
            section_text = section_match.group(1)
            
            # Para la tarifa residencial (caso especial)
            if section_name == 'Tarifa Residencial':
                for subsection in section_info['subsections']:
                    estrato_name = subsection['name']
                    if subsection['type'] == 'estrato':
                        # Buscar Rango 0 - CS
                        pattern = fr'{estrato_name}\.\s+Rango 0 - CS\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)'
                        match = re.search(pattern, section_text)
                        if match:
                            data.append({
                                'Sección': section_name,
                                'Subsección': estrato_name,
                                'Tipo': 'Rango 0 - CS',
                                'Propiedad EPM': float(match.group(1)),
                                'Propiedad Compartido': float(match.group(2)),
                                'Propiedad Cliente': float(match.group(3))
                            })
                        
                        # Buscar Rango > CS
                        pattern = fr'{estrato_name}.*?Rango > CS\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)'
                        match = re.search(pattern, section_text, re.DOTALL)
                        if match:
                            data.append({
                                'Sección': section_name,
                                'Subsección': estrato_name,
                                'Tipo': 'Rango > CS',
                                'Propiedad EPM': float(match.group(1)),
                                'Propiedad Compartido': float(match.group(2)),
                                'Propiedad Cliente': float(match.group(3))
                            })
                    else:  # Para consumo total
                        pattern = fr'{estrato_name}\.?\s+Todo el consumo\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)'
                        match = re.search(pattern, section_text)
                        if match:
                            data.append({
                                'Sección': section_name,
                                'Subsección': estrato_name,
                                'Tipo': 'Todo el consumo',
                                'Propiedad EPM': float(match.group(1)),
                                'Propiedad Compartido': float(match.group(2)),
                                'Propiedad Cliente': float(match.group(3))
                            })
            else:
                # Para las otras secciones
                for item in section_info['items']:
                    pattern = fr'{item}\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)'
                    match = re.search(pattern, section_text)
                    if match:
                        data.append({
                            'Sección': section_name,
                            'Subsección': item,
                            'Tipo': 'Valor único',
                            'Propiedad EPM': float(match.group(1)),
                            'Propiedad Compartido': float(match.group(2)),
                            'Propiedad Cliente': float(match.group(3))
                        })

    return pd.DataFrame(data)

def main():
    try:
        print("Leyendo el PDF...")
        pdf_path = '2014-12.pdf'
        pdf_text = extract_text_from_pdf(pdf_path)
        
        periodo_consumo = pdf_path.split('.')[0]
        

        print("Extrayendo datos...")
        df = extract_data(pdf_text)

        df['Periodo Consumo'] = periodo_consumo
        # Ordenar el DataFrame por sección y subsección
        df = df.sort_values(['Sección', 'Subsección', 'Tipo'])
        
        # Exportar a CSV
        output_file = f'{periodo_consumo}.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\nDatos exportados exitosamente a {output_file}")
        
        # Mostrar un resumen de los datos extraídos
        print("\nResumen de datos extraídos:")
        print(f"Total de registros: {len(df)}")
        print("\nSecciones encontradas:")
        for section in df['Sección'].unique():
            print(f"- {section}")
            subsections = df[df['Sección'] == section]['Subsección'].unique()
            for subsection in subsections:
                print(f"  └─ {subsection}")
        
    except FileNotFoundError:
        print("Error: No se encontró el archivo.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()