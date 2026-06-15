CREATE TABLE IF NOT EXISTS usuarios (
    id VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    saldo DECIMAL(10,2) DEFAULT 10000.00
);

CREATE TABLE IF NOT EXISTS transacciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario VARCHAR(50),
    tipo VARCHAR(10) NOT NULL,       
    activo VARCHAR(10) NOT NULL,     
    cantidad DECIMAL(10,2) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS portafolios (
    id_usuario VARCHAR(50),
    activo VARCHAR(10),
    cantidad DECIMAL(10,2) DEFAULT 0.00,
    precio_compra_promedio DECIMAL(10,2) DEFAULT 0.00,
    PRIMARY KEY (id_usuario, activo),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
);