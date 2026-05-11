-- phpMyAdmin SQL Dump
-- version 5.2.1deb3
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 11-05-2026 a las 00:03:41
-- Versión del servidor: 8.0.45-0ubuntu0.24.04.1
-- Versión de PHP: 8.3.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `db_tpr`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `categoria_id` int UNSIGNED NOT NULL,
  `nombre_categoria` varchar(55) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `tamano` enum('Pequeña','Mediana','Grande','Extragrande') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `imagen_categoria` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`categoria_id`, `nombre_categoria`, `tamano`, `imagen_categoria`) VALUES
(1, 'PIZZAS', '', 'plato1.png'),
(2, 'Sabores', '', 'plato1.png'),
(4, 'ASADOS', 'Mediana', 'asados1.png'),
(5, 'tamanos', 'Pequeña', 'plato1.png'),
(6, 'ADICIONES', 'Pequeña', 'platos/agregar.png'),
(7, 'HAMBURGUESAS', 'Pequeña', 'platos/hamburguesa.png'),
(8, 'PANZEROTI', 'Pequeña', 'panzeroti.png'),
(9, 'PICADAS', 'Pequeña', 'picadas.jpg');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `cliente_id` int UNSIGNED NOT NULL,
  `cc_cliente` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `nombre` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `telefono` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(76) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `rol` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'cliente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `clientes`
--

INSERT INTO `clientes` (`cliente_id`, `cc_cliente`, `nombre`, `telefono`, `email`, `rol`) VALUES
(1, '1192897316', 'Juan Bedoya', '3186506249', 'juandavidg347@gmail.com', 'cliente'),
(25, '1112150085', 'Juan Camilo Perez', '3154957442', 'lejuconso12@gmail.com', 'administrador'),
(37, '1192897318', 'Juan David Gonzalez Bedoya', '3186506249', 'juandavidg347@gmail.com', 'cliente'),
(39, '1109663994', 'Santiago Alexander Mejía Leito', '3116171425', 'santagomejia656@gmail.com', 'cliente'),
(41, '112215963', 'Daniela Alvarez', '3105036408', 'danielaalvar594@gmail.com', 'cliente'),
(46, '12345678', 'admin', '3000000001', 'admin@trespasos.com', 'administrador'),
(47, '87654321', 'cajero', '3000000002', 'cajero@trespasos.com', 'cajero'),
(50, '1234567891', 'Carlos Martinez Garcia', '3186506249', 'juandavidg347@gmail.com', 'cliente'),
(56, '1', 't', '1', 't@t.com', 'cliente'),
(57, '99', 'Test', '123', 't@t.com', 'cliente'),
(70, '123456', 'hjjkj', '3186506249', 'jujhjhjjjhhyhjjhjjuuu@gmail.com', 'cliente'),
(74, '114819751', 'Jean Luna', '3222656568', 'jeancarloslunaesquivel405@gmail.com', 'cliente'),
(75, '112150085', 'Juan Camilo Perez Hernandez', '3154957444', 'lejuconso12@gmail.com', 'cliente'),
(79, '1115094007', 'Juan Diego Sandoval', '3108329515', 'jhonespto@gmail.com', 'cliente'),
(80, '16161616', 'Af velasco', '3003003000', 'avelasco@mail.com', 'cliente'),
(81, '1111111111', 'juan', '2222222222', 'lejuconso12@gmail.com', 'cliente'),
(85, '94476464', 'Arcano Digital ', '3183000001', 'juanc.posada@outlook.com', 'cliente'),
(86, '39542846', 'JC Posadita', '3003001020', 'posadita123@gmail.com', 'cliente'),
(87, '1112200451', 'Jhan Mejía Torres', '1324560184', 'tengohambre@casanas.com', 'cliente'),
(95, '7777777777', 'juanC', '9999999999', 'lejuconso12@gmail.com', 'cliente'),
(99, '5555555555', 'Juan', '9999999999', 'lejuconso12@gmail.com', 'cliente'),
(105, '1192897311', 'Juan David González', '3186506249', 'juandavidg347@gmail.com', 'cliente'),
(126, '1192867318', 'Posadita', '3186506246', 'juandavidg347@gmail.com', 'cliente'),
(135, '1112377256', 'Felipe casañas', '3026029365', 'casanascastrofelipe@gmail.com', 'cliente'),
(137, '1101111111', 'Posada', '3186506249', 'casanascastrofelipe@gmail.com', 'cliente'),
(138, '1313131331', 'David Bedoya', '3186506249', 'juandavidg347@gmail.com', 'cliente'),
(139, '3226453050', 'Samuel Alexis Delgado', '3226453050', 'samuelalexis1013@gmail.com', 'cliente'),
(148, '2222222222', 'Juan', '2222222222', 'lejuconso12@gmail.com', 'cliente'),
(153, '1122334455', 'Diego Pinilla', '3173173177', 'diego@diego.com', 'cliente'),
(154, '1112391677', 'Samuel', '3186506249', 'juandavidg347@gmail.com', 'cliente'),
(156, '2911111461', 'Juan', '3546985321', 'kilo12345678@gmail.com', 'cliente'),
(157, '1088313105', 'Carolina Durango', '3206122140', 'cdurango@sena.edu.co', 'cliente'),
(158, '1000000', 'Yosito lindo', '3010000000', 'jfkalnfjs@sena.edu.co', 'cliente'),
(159, '16860954', 'Andres Felipe Vivas Erazo', '3122775658', 'vivasandres802@gmail.com', 'cliente'),
(162, '1192897731', 'Juan David Gonzalez Bedoya', '3186506249', 'juandavidg347@gmail.com', 'cliente');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalles_domicilios`
--

CREATE TABLE `detalles_domicilios` (
  `detalle_id` int UNSIGNED NOT NULL,
  `domicilio_id` int UNSIGNED NOT NULL,
  `producto_id` int UNSIGNED NOT NULL,
  `cantidad` int NOT NULL,
  `valor_unitario` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `detalles_domicilios`
--

INSERT INTO `detalles_domicilios` (`detalle_id`, `domicilio_id`, `producto_id`, `cantidad`, `valor_unitario`) VALUES
(38, 28, 44, 1, 214000),
(39, 29, 43, 4, 50000),
(40, 30, 44, 1, 356000);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalles_reservas`
--

CREATE TABLE `detalles_reservas` (
  `pedido_id` int UNSIGNED NOT NULL,
  `reserva_id` int UNSIGNED NOT NULL,
  `producto_id` int UNSIGNED NOT NULL,
  `cantidad` int NOT NULL,
  `valor_unitario` int NOT NULL,
  `notas` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `detalles_reservas`
--

INSERT INTO `detalles_reservas` (`pedido_id`, `reserva_id`, `producto_id`, `cantidad`, `valor_unitario`, `notas`) VALUES
(61, 81, 42, 1, 58000, 'EXTRA GRANDE | Adicionales: Extra Queso (x1)'),
(62, 82, 43, 1, 154000, 'EXTRA GRANDE | Adicionales: Extra Queso (x1), Piña (x10), Champiñones (x1), Pimientos (x1)'),
(63, 83, 14, 1, 66000, NULL),
(66, 85, 13, 1, 29000, 'MEDIANA | Sabores: Hawaiana'),
(67, 85, 13, 1, 16000, 'PERSONAL'),
(68, 86, 34, 1, 20000, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `domicilios`
--

CREATE TABLE `domicilios` (
  `domicilio_id` int UNSIGNED NOT NULL,
  `cliente_id` int UNSIGNED NOT NULL,
  `direccion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `fecha_hora` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `pago_transferencia` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `estado_pedido` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `comprobante_transferencia` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `domicilios`
--

INSERT INTO `domicilios` (`domicilio_id`, `cliente_id`, `direccion`, `fecha_hora`, `pago_transferencia`, `estado_pedido`, `comprobante_transferencia`) VALUES
(28, 25, 'Calle 23 #23-22, Prueba', '2026-03-26 20:35:00', '1', 'En preparación', NULL),
(29, 158, 'cra 34 # 56-78, Busquela con encuentrela', '2026-03-27 15:09:38', '1', 'En revisión', 'comprobantes/comprobante_dom_1000000.png'),
(30, 159, 'Sena, Senasofia plus', '2026-03-27 21:22:11', '0', 'Pendiente', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mesas`
--

CREATE TABLE `mesas` (
  `mesa_id` int UNSIGNED NOT NULL,
  `num_mesa` int NOT NULL,
  `piso` int NOT NULL,
  `estado` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `numero_mesa` int NOT NULL DEFAULT '0',
  `capacidad` int NOT NULL DEFAULT '4'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `mesas`
--

INSERT INTO `mesas` (`mesa_id`, `num_mesa`, `piso`, `estado`, `numero_mesa`, `capacidad`) VALUES
(4, 1, 2, 'disponible', 4, 4),
(5, 2, 2, 'disponible', 1, 4),
(6, 10, 1, 'disponible', 6, 4),
(7, 11, 1, 'disponible', 7, 4),
(8, 20, 2, 'disponible', 8, 4),
(9, 21, 2, 'disponible', 9, 4);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedido_detalles_sabores`
--

CREATE TABLE `pedido_detalles_sabores` (
  `composicion_id` int UNSIGNED NOT NULL,
  `sabor_id` int UNSIGNED NOT NULL,
  `detalle_reserva_id` int UNSIGNED DEFAULT NULL,
  `detalle_domicilio_id` int UNSIGNED DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `precios_tamano`
--

CREATE TABLE `precios_tamano` (
  `id` int NOT NULL,
  `producto_id` int NOT NULL,
  `tamano_id` int NOT NULL,
  `precio` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Volcado de datos para la tabla `precios_tamano`
--

INSERT INTO `precios_tamano` (`id`, `producto_id`, `tamano_id`, `precio`) VALUES
(2, 14, 23, 58000.00),
(8, 13, 23, 16000.00),
(18, 42, 23, 20000.00),
(20, 45, 23, 35000.00),
(25, 44, 23, 20000.00),
(26, 46, 23, 180000.00),
(27, 46, 24, 50000.00),
(28, 46, 25, 50000.00),
(29, 46, 26, 1800000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `producto_id` int UNSIGNED NOT NULL,
  `nombre_producto` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `categoria_id` int UNSIGNED NOT NULL,
  `descripcion_producto` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `precio_base` int NOT NULL,
  `disponibilidad_producto` tinyint(1) NOT NULL DEFAULT '1',
  `imagen_producto` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `stock` int NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`producto_id`, `nombre_producto`, `categoria_id`, `descripcion_producto`, `precio_base`, `disponibilidad_producto`, `imagen_producto`, `stock`) VALUES
(13, 'Pizza Hawaina', 1, 'Capacidad: 1 sabor', 16000, 1, 'plato1.png', 0),
(14, 'Pizza Peperonni', 1, 'Capacidad: 3 sabores', 58000, 1, 'peperoni.png', 0),
(15, 'Hawaiana', 2, 'Piña y jamón', 1000, 1, NULL, 0),
(16, 'Jamón y Queso', 2, 'Clásica', 1000, 1, NULL, 0),
(17, 'Champiñones', 2, 'Champiñones frescos', 1000, 1, NULL, 0),
(23, 'Personal', 5, 'Capacidad: 1 sabor', 18000, 1, NULL, 0),
(24, 'Mediana', 5, 'Capacidad: 2 sabores', 28000, 1, NULL, 0),
(25, 'Grande', 5, 'Capacidad: 3 sabores', 38000, 1, NULL, 0),
(26, 'Extra Grande', 5, 'Capacidad: 4 sabores', 50000, 1, NULL, 0),
(27, 'Extra Queso', 6, 'Porción de queso extra', 8000, 1, NULL, 10),
(28, 'Piña', 6, 'Piña fresca', 8000, 1, NULL, 10),
(29, 'Champiñones', 6, 'Champiñones frescos', 8000, 1, NULL, 12),
(30, 'Pimientos', 6, 'Pimientos frescos', 8000, 1, NULL, 10),
(34, 'Filete de pollo', 4, '', 20000, 1, 'platos/Tipos-de-asados1.png', 0),
(42, 'Pizza estofada', 1, '', 20000, 1, 'platos/estofada.png', 0),
(43, 'pizza napolitana', 1, 'deliciosa', 0, 1, 'platos/pizaaa.png', 0),
(44, 'pizza favo', 1, 'deliciosa', 20000, 1, 'platos/favo.png', 0),
(45, 'pizza con queso', 1, 'no tiene queso 1234', 35000, 1, 'platos/queso.png', 0),
(46, 'Pizza', 1, '', 180000, 1, 'platos/pizaaaa.png', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reservas`
--

CREATE TABLE `reservas` (
  `reserva_id` int UNSIGNED NOT NULL,
  `cliente_id` int UNSIGNED NOT NULL,
  `mesa_id` int UNSIGNED NOT NULL,
  `cantidad_personas` int NOT NULL,
  `tematica_id` int UNSIGNED NOT NULL,
  `fecha_hora` datetime NOT NULL,
  `estado` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `pago_transferencia` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `comprobante_transferencia` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `reservas`
--

INSERT INTO `reservas` (`reserva_id`, `cliente_id`, `mesa_id`, `cantidad_personas`, `tematica_id`, `fecha_hora`, `estado`, `pago_transferencia`, `comprobante_transferencia`) VALUES
(80, 153, 4, 5, 5, '2026-03-31 07:00:00', 'confirmada', '0', NULL),
(81, 154, 4, 2, 5, '2026-03-29 21:00:00', 'confirmada', '0', NULL),
(82, 156, 4, 8, 6, '2026-04-15 23:00:00', 'en espera', '1', NULL),
(83, 157, 4, 2, 5, '2026-03-29 08:00:00', 'confirmada', '0', NULL),
(85, 37, 5, 12, 5, '2026-04-26 18:00:00', 'confirmada', '0', NULL),
(86, 162, 6, 1, 5, '2026-05-11 20:00:00', 'confirmada', '0', NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tematicas`
--

CREATE TABLE `tematicas` (
  `tematica_id` int UNSIGNED NOT NULL,
  `nombre_tematica` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `valor_tematica` int NOT NULL DEFAULT '0',
  `activo` tinyint(1) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tematicas`
--

INSERT INTO `tematicas` (`tematica_id`, `nombre_tematica`, `valor_tematica`, `activo`) VALUES
(4, 'Ninguna', 15000, 1),
(5, 'Aniversario', 20000, 1),
(6, 'Cumpleaños', 0, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `usuario_id` int UNSIGNED NOT NULL,
  `cc_usuario` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `nombre` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `apellidos` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `telefono` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `rol` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT '1',
  `email` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `contrasena` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`usuario_id`, `cc_usuario`, `nombre`, `apellidos`, `telefono`, `rol`, `estado`, `email`, `contrasena`) VALUES
(1, '12345678', 'Juan', 'Bedoya', '3186506249', 'administrador', 1, 'juandavidg347@gmail.com', 'admin'),
(2, '123456789', 'Cajero', 'Martinez', '31865000', 'cajero', 1, 'sssss@gmail.com', 'cajero'),
(3, '1112150085', 'Juan Camilo ', 'Perez', '3154957442', 'administrador', 1, 'lejuconso12@gmail.com', 'Admin1'),
(4, '1109663994', 'Santiago ', 'Mejia', '3116171425', 'administrador', 1, 'santagomejia656@gmail.com', 'admin1');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`categoria_id`);

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`cliente_id`),
  ADD UNIQUE KEY `cc_cliente` (`cc_cliente`);

--
-- Indices de la tabla `detalles_domicilios`
--
ALTER TABLE `detalles_domicilios`
  ADD PRIMARY KEY (`detalle_id`),
  ADD KEY `domicilio_id` (`domicilio_id`),
  ADD KEY `producto_id` (`producto_id`);

--
-- Indices de la tabla `detalles_reservas`
--
ALTER TABLE `detalles_reservas`
  ADD PRIMARY KEY (`pedido_id`),
  ADD KEY `reserva_id` (`reserva_id`),
  ADD KEY `producto_id` (`producto_id`);

--
-- Indices de la tabla `domicilios`
--
ALTER TABLE `domicilios`
  ADD PRIMARY KEY (`domicilio_id`),
  ADD KEY `cliente_id` (`cliente_id`);

--
-- Indices de la tabla `mesas`
--
ALTER TABLE `mesas`
  ADD PRIMARY KEY (`mesa_id`),
  ADD UNIQUE KEY `num_mesa` (`num_mesa`);

--
-- Indices de la tabla `pedido_detalles_sabores`
--
ALTER TABLE `pedido_detalles_sabores`
  ADD PRIMARY KEY (`composicion_id`),
  ADD KEY `sabor_id` (`sabor_id`),
  ADD KEY `detalle_reserva_id` (`detalle_reserva_id`),
  ADD KEY `detalle_domicilio_id` (`detalle_domicilio_id`);

--
-- Indices de la tabla `precios_tamano`
--
ALTER TABLE `precios_tamano`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uk_producto_tamano` (`producto_id`,`tamano_id`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`producto_id`),
  ADD KEY `categoria_id` (`categoria_id`);

--
-- Indices de la tabla `reservas`
--
ALTER TABLE `reservas`
  ADD PRIMARY KEY (`reserva_id`),
  ADD KEY `cliente_id` (`cliente_id`),
  ADD KEY `mesa_id` (`mesa_id`),
  ADD KEY `tematica_id` (`tematica_id`);

--
-- Indices de la tabla `tematicas`
--
ALTER TABLE `tematicas`
  ADD PRIMARY KEY (`tematica_id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`usuario_id`),
  ADD UNIQUE KEY `cc_usuario` (`cc_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `categoria_id` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `cliente_id` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=163;

--
-- AUTO_INCREMENT de la tabla `detalles_domicilios`
--
ALTER TABLE `detalles_domicilios`
  MODIFY `detalle_id` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT de la tabla `detalles_reservas`
--
ALTER TABLE `detalles_reservas`
  MODIFY `pedido_id` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=69;

--
-- AUTO_INCREMENT de la tabla `domicilios`
--
ALTER TABLE `domicilios`
  MODIFY `domicilio_id` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT de la tabla `mesas`
--
ALTER TABLE `mesas`
  MODIFY `mesa_id` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `pedido_detalles_sabores`
--
ALTER TABLE `pedido_detalles_sabores`
  MODIFY `composicion_id` int UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `precios_tamano`
--
ALTER TABLE `precios_tamano`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `producto_id` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=47;

--
-- AUTO_INCREMENT de la tabla `reservas`
--
ALTER TABLE `reservas`
  MODIFY `reserva_id` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=87;

--
-- AUTO_INCREMENT de la tabla `tematicas`
--
ALTER TABLE `tematicas`
  MODIFY `tematica_id` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `usuario_id` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `detalles_domicilios`
--
ALTER TABLE `detalles_domicilios`
  ADD CONSTRAINT `detalles_domicilios_ibfk_1` FOREIGN KEY (`domicilio_id`) REFERENCES `domicilios` (`domicilio_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `detalles_domicilios_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`producto_id`);

--
-- Filtros para la tabla `detalles_reservas`
--
ALTER TABLE `detalles_reservas`
  ADD CONSTRAINT `detalles_reservas_ibfk_1` FOREIGN KEY (`reserva_id`) REFERENCES `reservas` (`reserva_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `detalles_reservas_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`producto_id`);

--
-- Filtros para la tabla `domicilios`
--
ALTER TABLE `domicilios`
  ADD CONSTRAINT `domicilios_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`cliente_id`);

--
-- Filtros para la tabla `pedido_detalles_sabores`
--
ALTER TABLE `pedido_detalles_sabores`
  ADD CONSTRAINT `pedido_detalles_sabores_ibfk_1` FOREIGN KEY (`sabor_id`) REFERENCES `productos` (`producto_id`),
  ADD CONSTRAINT `pedido_detalles_sabores_ibfk_2` FOREIGN KEY (`detalle_reserva_id`) REFERENCES `detalles_reservas` (`pedido_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `pedido_detalles_sabores_ibfk_3` FOREIGN KEY (`detalle_domicilio_id`) REFERENCES `detalles_domicilios` (`detalle_id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `productos`
--
ALTER TABLE `productos`
  ADD CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`categoria_id`);

--
-- Filtros para la tabla `reservas`
--
ALTER TABLE `reservas`
  ADD CONSTRAINT `reservas_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`cliente_id`),
  ADD CONSTRAINT `reservas_ibfk_2` FOREIGN KEY (`mesa_id`) REFERENCES `mesas` (`mesa_id`),
  ADD CONSTRAINT `reservas_ibfk_3` FOREIGN KEY (`tematica_id`) REFERENCES `tematicas` (`tematica_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
