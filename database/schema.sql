CREATE DATABASE IF NOT EXISTS ARGBROKER;
USE ARGBROKER;

SET GLOBAL event_scheduler = ON;

CREATE TABLE IF NOT EXISTS usuarios (
    id VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    saldo DECIMAL(10,2) DEFAULT 10000.00
);

CREATE TABLE IF NOT EXISTS activos (
    ticker VARCHAR(10) PRIMARY KEY,
    precio_actual DECIMAL(15, 2) NOT NULL DEFAULT 100.00
);

CREATE TABLE IF NOT EXISTS portafolios (
    id_usuario VARCHAR(50),
    activo VARCHAR(10),
    cantidad DECIMAL(10,2) DEFAULT 0.00,
    precio_compra_promedio DECIMAL(10,2) DEFAULT 0.00,
    PRIMARY KEY (id_usuario, activo),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (activo) REFERENCES activos(ticker) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transacciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario VARCHAR(50),
    tipo ENUM('COMPRA', 'VENTA') NOT NULL,        
    activo VARCHAR(10) NOT NULL,   
    cantidad DECIMAL(10,2) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE OR REPLACE VIEW vista_rendimiento AS
SELECT 
    p.id_usuario,
    p.activo,
    p.cantidad,
    p.precio_compra_promedio,
    a.precio_actual,
    ((a.precio_actual - p.precio_compra_promedio) / p.precio_compra_promedio) * 100 AS porcentaje_rendimiento,
    (a.precio_actual - p.precio_compra_promedio) * p.cantidad AS ganancia_perdida_total
FROM portafolios p
JOIN activos a ON p.activo = a.ticker;

DROP EVENT IF EXISTS actualizar_mercado_constante;

DELIMITER //

CREATE EVENT actualizar_mercado_constante
ON SCHEDULE EVERY 1 SECOND
DO
  BEGIN
    UPDATE activos 
    SET precio_actual = ROUND(precio_actual * (1 + (RAND() * 0.04 - 0.02)), 2);
  END //

DELIMITER ;

SELECT "Base de datos ARGBROKER inicializada correctamente." AS status;