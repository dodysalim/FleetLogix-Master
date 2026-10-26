# 🎨 Guía Visual · FleetLogix Dashboard (Streamlit)

Recorrido página por página de las 5 vistas del dashboard corporativo.

---

## 📐 Diseño global

| Atributo | Valor |
|----------|-------|
| Framework | Streamlit 1.36 · wide layout |
| Tema | Oscuro corporativo (cyan `#4CC9F0` + teal `#00D4AA` + ámbar `#F8B400` + fondo `#0E1117`) |
| Tipografía | Inter / system-ui · 12pt body · 18pt títulos · 30pt KPI cards |
| Gráficos | Plotly 5.22 con template `plotly_dark` personalizado |
| Sidebar global | Rango de fechas · health-check de BD · botón de refresh · última actualización |
| Interactividad | Tabs por sección · filtros por página · descarga CSV · hover unificado |
| Caché | `@st.cache_data(ttl=300)` → 5 minutos por query |

---

## Página 1 · 📊 Resumen Ejecutivo

> **Audiencia:** Dirección general · CEO/COO
> **Pregunta que responde:** *¿Cómo va la operación esta semana / mes / trimestre?*
> **Fuente:** `v_kpi_executive` · `v_deliveries_timeseries`

### Fila 1 (6 KPIs operativos)
| Tarjeta | Fuente | Color |
|---------|--------|-------|
| Vehículos activos | `v_kpi_executive.active_vehicles` | info (cyan) |
| Conductores activos | `active_drivers` | info |
| Viajes completados | `completed_trips` | success (teal) |
| Entregas realizadas | `delivered` | success |
| On-Time Rate | `on_time_rate_pct` | semáforo (≥85 success, ≥70 warn, <70 danger) |
| Total toneladas | `total_tons` | info |

### Fila 2 (4 KPIs de excepciones)
| Tarjeta | Fuente | Color |
|---------|--------|-------|
| Entregas pendientes | `pending_deliveries` | warn |
| Entregas fallidas | `failed_deliveries` | danger si >100 |
| Mantenimiento próximo (30d) | `vehicles_maintenance_30d` | warn |
| Costo de mantenimiento | `total_maintenance_cost` | info |

### Tabs analíticos
- **📈 Tendencia diaria** — Área-stacked (delivered/pending/failed) sobre `v_deliveries_timeseries`
- **🥧 Distribución de estados** — Donut + tabla con % del total
- **📊 Volumen vs Peso** — Bars de cantidad + línea de peso en eje secundario

---

## Página 2 · 🚚 Flota

> **Audiencia:** Jefe de flota · Operaciones
> **Pregunta que responde:** *¿Qué vehículos están sobrecargados / subutilizados? ¿Cuáles tienen mantenimiento vencido?*
> **Fuente:** `v_vehicle_performance` · `v_maintenance_alerts`

### KPIs (5 tarjetas)
Vehículos totales · Activos · En mantenimiento · Alertas críticas · Utilización promedio.

### Filtros
Tipo de vehículo (multiselect) · Tipo de combustible (multiselect).

### Tabs
- **📊 Top vehículos** — Bar horizontal top 15 por viajes completados, coloreado por tipo
- **🎯 Scatter eficiencia** — X: L/100km · Y: % utilización · Tamaño: total viajes · Color: tipo
- **🛠 Alertas de mantenimiento** — Bar de niveles (VENCIDO / ESTA SEMANA / ESTE MES / OK) + tabla + botón CSV

### Detalle
Tabla completa con 12 columnas (placa, tipo, combustible, capacidad, viajes, utilización, eficiencia…).

---

## Página 3 · 👨‍✈️ Conductores

> **Audiencia:** RRHH · Supervisor de operaciones
> **Pregunta que responde:** *¿Qué conductores destacan? ¿Cuáles tienen licencia por vencer?*
> **Fuente:** `v_driver_performance`

### KPIs (5 tarjetas)
Total · Activos · Licencias vencidas · Por vencer (30d) · Tasa de éxito promedio.

### Filtros
Estado del contrato · slider "Top N" (5–30).

### Tabs
- **🏆 Top por viajes** — Bar horizontal con color por % éxito (rojo → ámbar → teal)
- **✅ Tasa de éxito** — Ranking de top-N por `success_rate_pct` (mínimo 10 entregas para significancia)
- **🪪 Alertas de licencia** — Donut (Vigente/Por vencer/Vencida) + tabla filtrada

### Detalle
Tabla con 11 columnas + botón CSV.

---

## Página 4 · 🛣️ Rutas

> **Audiencia:** Planning · Logística
> **Pregunta que responde:** *¿Qué corredores consumen más? ¿Hay rutas rentables/poco eficientes?*
> **Fuente:** `v_route_traffic`

### KPIs (5 tarjetas)
Rutas activas · Viajes totales · Km recorridos · Combustible total · Eficiencia media.

### Filtros
Ciudad origen (multiselect) · slider "Top N".

### Tabs
- **📊 Top rutas por tráfico** — Bar horizontal con color por distancia
- **⛽ Eficiencia por ruta** — Scatter X: distancia · Y: L/100km · Tamaño: viajes · Color: origen
- **📋 Detalle** — Tabla con 14 columnas + CSV

---

## Página 5 · ⛽ Combustible

> **Audiencia:** Sostenibilidad · Finanzas
> **Pregunta que responde:** *¿Cómo evoluciona el consumo? ¿Qué tipo de vehículo es más eficiente?*
> **Fuente:** `v_fuel_efficiency`

### KPIs (5 tarjetas)
Total combustible · Total distancia · Eficiencia global · Viajes con consumo · Meses con datos.

### Tabs
- **📈 Tendencia mensual** — Bars de combustible + línea de L/100km (doble eje)
- **🚚 Eficiencia por tipo** — Dos bars side-by-side (eficiencia ordenada · volumen de viajes)
- **🥧 Composición por combustible** — Dos donuts (litros consumidos · viajes por fuel_type)
- **📋 Datos** — Tabla mensual + CSV

---

## 🎯 Criterios de diseño

1. **Densidad informativa** — Cada página responde una pregunta de negocio clara.
2. **Jerarquía visual** — KPIs arriba · Gráficos en tabs · Tabla detalle al final.
3. **Semáforos contextuales** — Colores variantes (`success`/`warn`/`danger`) en tarjetas según umbrales.
4. **Drill-down opcional** — Todas las tablas son interactivas (sort, search) y permiten exportar CSV.
5. **Performance** — Caché de 5 min evita hits repetidos a la BD en la misma sesión.
6. **Accesibilidad** — Tema oscuro con contraste AAA · tooltips descriptivos.

---

## 📸 Capturas recomendadas para la entrega

Guardar en `dashboard/screenshots/`:

| Archivo | Contenido |
|---------|-----------|
| `00_modelo.png` | Diagrama del star schema |
| `01_resumen_ejecutivo.png` | Página 1 con las 10 tarjetas visibles + tab "Tendencia" |
| `02_flota.png` | Scatter de eficiencia visible |
| `03_conductores.png` | Top 15 conductores por viajes |
| `04_rutas.png` | Scatter de rutas por distancia |
| `05_combustible.png` | Tendencia mensual con doble eje |
