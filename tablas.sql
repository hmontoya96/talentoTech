-- Tabla: Tarifas
CREATE TABLE Tarifas (
    id_tarifa INT AUTO_INCREMENT PRIMARY KEY,
    seccion VARCHAR(255) NOT NULL,
    subseccion VARCHAR(255),
    tipo VARCHAR(255)
);

-- Tabla: Tarifas_Valores
CREATE TABLE Tarifas_Valores (
    id_valor INT AUTO_INCREMENT PRIMARY KEY,
    id_tarifa INT,
    propiedad_epm DECIMAL(10,2),
    propiedad_compartido DECIMAL(10,2),
    propiedad_cliente DECIMAL(10,2),
    periodo_consumo DATE,
    FOREIGN KEY (id_tarifa) REFERENCES Tarifas(id_tarifa)
);

-- Tabla opcional: Rangos_Consumo
CREATE TABLE Rangos_Consumo (
    id_rango INT AUTO_INCREMENT PRIMARY KEY,
    id_tarifa INT,
    rango VARCHAR(255),
    FOREIGN KEY (id_tarifa) REFERENCES Tarifas(id_tarifa)
);
