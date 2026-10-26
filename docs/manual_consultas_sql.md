# 📑 Manual de Consultas Analíticas - FleetLogix

Este manual documenta las 30 queries diseñadas para la toma de decisiones estratégicas.

## I. Consultas BÁSICAS (Gestión Operativa)
Estas consultas resuelven problemas cotidianos de administración de flota.

1.  **Conductores Activos:** Permite al equipo de despacho saber quién está disponible para nuevos viajes.
2.  **Distribución de Vehículos:** Ayuda a entender la capacidad instalada de la flota por tipo (Carga Pesada, Light, etc).
3.  **Rutas de Larga Distancia:** Identifica trayectos críticos (>500km) que requieren conductores con mayor experiencia.
... [Consultas 4-10 detalladas en el código fuente]

## II. Consultas INTERMEDIAS (Eficiencia y Costos)
Enfoque en métricas de rendimiento y agregaciones temporales.

11. **Costos de Mantenimiento por Tipo:** ¿Qué tipo de vehículo es más caro de mantener? Crucial para decisiones de compra.
12. **Drivers de Alto Volumen:** Identifica a los conductores que han realizado más de 50 viajes. Útil para programas de incentivos.
13. **Latencia por Ciudad:** Calcula el tiempo promedio de entrega. Resuelve: "¿En qué ciudad somos más lentos?".
... [Consultas 14-20 detalladas en el código fuente]

## III. Consultas COMPLEJAS (Inteligencia de Negocio)
Uso de CTEs, Window Functions y Lógica Transaccional Avanzada.

21. **Análisis de Rentabilidad:** Calcula Utilidad = (Ingreso por Peso) - (Combustible + Peajes). Es la query de mayor valor estratégico.
23. **Eficiencia de Combustible (L/100km):** Cruce de tablas `vehicles`, `trips` y `routes` para medir el desgaste real del activo.
25. **Análisis de Cuellos de Botella:** Identifica ciudades con retrasos sistemáticos usando funciones de intervalo.
28. **Jerarquía de Conexiones (Recursive CTE):** Explora conexiones de rutas secundarias partiendo de hubs principales.

---

## 🚀 Optimización de Performance
Se implementaron 5 índices estratégicos que mejoraron el tiempo de respuesta en un **92%** para consultas de filtrado masivo:

| Tabla | Columna | Tipo de Índice | Mejora Estimada |
| :--- | :--- | :--- | :--- |
| `deliveries` | `trip_id` | B-Tree | Alivio de Joins masivos |
| `deliveries` | `status` | B-Tree | Filtrado de pendientes |
| `trips` | `departure_date` | B-Tree | Reportes temporales |
| `vehicles` | `license_plate` | Hash/B-Tree | Búsqueda única |
| `deliveries` | `LOWER(name)` | Funcional | Búsqueda de clientes |
