# 📚 Documentación FleetLogix Master
### Centro de Conocimiento Técnico — Nivel Empresarial

---

> **Navegación Rápida**
> 
> - 📖 [README Principal](../README.md) — Visión general + instalación
> - 🔧 [Documentación Técnica Completa](PI_M2_DOCUMENTATION_DODY.md) — Manual exhaustivo (1,447 líneas)
> - ☁️ [Arquitectura AWS & IoT](arquitectura_tecnica.md) — Cloud + Serverless
> - 📊 [Dashboard & KPIs](../dashboard/README.md) — Visualización analítica
> - 🗄️ [Diccionario de Datos](diccionario_de_datos.md) — Modelo relacional
> - 💾 [Manual SQL](manual_consultas_sql.md) — 50+ queries optimizadas
> - ✅ [Checklist Entrega](CHECKLIST_ENTREGA.md) — Cumplimiento M2

---

## 📋 Índice de Documentos

### 🎯 Nivel 1 — Introducción y Visión
| Documento | Descripción | Páginas |
|-----------|-------------|---------|
| **[README Principal](../README.md)** | Visión general, arquitectura, instalación, KPIs | 90+ |
| **[Setup Guide](setup_guide.md)** | Guía paso a paso de despliegue | 15+ |
| **[Guía Visual](../dashboard/docs/GUIA_VISUAL.md)** | Tour por el dashboard | 12+ |

---

### 🔬 Nivel 2 — Arquitectura y Diseño
| Documento | Descripción | Páginas |
|-----------|-------------|---------|
| **[Arquitectura Técnica](arquitectura_tecnica.md)** | Diagramas AWS, IoT, CloudWatch, costos | 40+ |
| **[Modelo de Datos](../dashboard/MODELO_DATOS.md)** | ERD + relaciones entidades | 10+ |
| **[Star Schema](senior_architecture.md)** | Diseño dimensional Snowflake | 25+ |

---

### 💻 Nivel 3 — Implementación Técnica
| Documento | Descripción | Páginas |
|-----------|-------------|---------|
| **[Documentación M2](PI_M2_DOCUMENTATION_DODY.md)** | Manual exhaustivo (Senior Level) | **1,378** |
| **[Diccionario de Datos](diccionario_de_datos.md)** | Tablas, columnas, tipos, constraints | 15+ |
| **[Manual SQL](manual_consultas_sql.md)** | Queries: básico → avanzado + optimización | **50+** |
| **[API PostgREST](../dashboard/setup/README.md)** | REST automático + JWT + ejemplos | 10+ |

---

### 📈 Nivel 4 — Análisis y Business Intelligence
| Documento | Descripción | Páginas |
|-----------|-------------|---------|
| **[KPIs](../dashboard/KPIs.md)** | Métricas operativas + fórmulas | 12+ |
| **[Evidencia Ejecución](evidencia_ejecucion/)** | Capturas + logs + reportes AWS | 30+ |
| **[AWS Simulation](../dashboard/data_exports/README.md)** | Reportes automatizados | 8+ |

---

## 🔍 Búsqueda Rápida por Tema

### 🗄️ **Bases de Datos**
- 📂 **PostgreSQL:** [Optimización índices](manual_consultas_sql.md#4-optimización-de-índices), [Window Functions](manual_consultas_sql.md#3-queries-con-window-functions), [CTE Recursivas](manual_consultas_sql.md#2-queries-avanzadas-con-cte)
- ☁️ **Snowflake:** [Star Schema](PI_M2_DOCUMENTATION_DODY.md#6-estructuración-del-motor-analítico), [Consultas analíticas](PI_M2_DOCUMENTATION_DODY.md#6.3-consultas-analíticas-en-snowflake)
- 🗃️ **MongoDB:** [Telemetría IoT](PI_M2_DOCUMENTATION_DODY.md#7-telemetría-iot-híbrida), [Time Series](arquitectura_tecnica.md)

### ☁️ **Cloud & DevOps**
- ⚡ **AWS Lambda:** [Funciones serverless](PI_M2_DOCUMENTATION_DODY.md#8.2.2-función-lambda), [CloudWatch](arquitectura_tecnica.md#3-monitoreo-estratégico)
- 📦 **S3:** [Data lake + lifecycle](PI_M2_DOCUMENTATION_DODY.md#8.2.1-s3-con-lifecycle-policies)
- 🔄 **Docker:** [Compose files](../docker/docker-compose.yml), [PostgREST](../docker/postgrest/Dockerfile)

### 📊 **Business Intelligence**
- 📈 **Streamlit:** [Dashboard code](../dashboard/app.py), [Componentes](PI_M2_DOCUMENTATION_DODY.md#9.2-dashboard-en-streamlit)
- 📉 **Power BI:** [Reportes ejecutivos](../dashboard/data_exports/README.md)
- 📋 **KPIs:** [On-Time Rate](KPIs.md#1-on-time-delivery-rate-ontime-rate), [Fuel Efficiency](KPIs.md#2-fuel-efficiency)

### 🔧 **APIs & Integraciones**
- 🔌 **PostgREST:** [Configuración](../dashboard/setup/README.md), [Endpoints](PI_M2_DOCUMENTATION_DODY.md#10.3-endpoints-generados)
- 🌐 **API Gateway:** [Integración Lambda](arquitectura_tecnica.md#1-diagrama-de-flujo-de-datos)
- 📡 **IoT Core:** [Simulación GPS](aws_local_simulation.md)

---

## 📂 Documentación por Avance M2

### Avance 1 — Generación de Datos
| Requisito | Documento | Estado |
|-----------|-----------|--------|
| +500K registros | `scripts/generate_synthetic_data.py` | ✅ |
| 6 tablas relacionadas | `sql/schema.sql` | ✅ |
| Diversidad de datos | [Evidencia](evidencia_ejecucion/evidencia_generacion.md) | ✅ |

### Avance 2 — Queries Analíticas
| Requisito | Documento | Estado |
|-----------|-----------|--------|
| 5 queries básicas | [Manual SQL → Sección 1](manual_consultas_sql.md) | ✅ |
| 4 avanzadas (Window/CTE) | [Manual SQL → Sección 2](manual_consultas_sql.md#2-queries-avanzadas-con-cte) | ✅ |
| 3 optimizadas | [Manual SQL → Sección 4](manual_consultas_sql.md#4-optimización-de-índices) | ✅ |

### Avance 3 — Modelo Dimensional
| Requisito | Documento | Estado |
|-----------|-----------|--------|
| Star Schema en Snowflake | [Snowflake DDL](PI_M2_DOCUMENTATION_DODY.md#6.2-esquema-dimensional-en-snowflake) | ✅ |
| ETL automatizado | `scripts/etl_to_snowflake.py` | ✅ |
| 3 queries con hechos/dimensiones | [Ejemplos](PI_M2_DOCUMENTATION_DODY.md#6.3-consultas-analíticas) | ✅ |

### Avance 4 — Cloud Serverless
| Requisito | Documento | Estado |
|-----------|-----------|--------|
| AWS Lambda + API Gateway | [Arquitectura](arquitectura_tecnica.md) | ✅ |
| DynamoDB o S3 | `lambda_functions/` + [Config](PI_M2_DOCUMENTATION_DODY.md#8) | ✅ |
| CloudWatch Dashboard | [Reporte](evidencia_ejecucion/aws_simulation/) | ✅ |

---

## 🎓 Conceptos Técnicos Explicados

###基礎 (Fundamentals)
- **OLTP vs OLAP:** [Arquitectura → 2.1](arquitectura_tecnica.md#21-la-tiranía-del-oltp-contra-el-olap)
- **ETL Pipeline:** [Documentación M2 → 5.1](PI_M2_DOCUMENTATION_DODY.md#51-arquitectura-del-pipeline)
- **Star Schema:** [Documentación M2 → 2.3](PI_M2_DOCUMENTATION_DODY.md#23-la-necesidad-del-modelado-star-schema)

###中級 (Intermediate)
- **Window Functions:** `ROW_NUMBER()`, `RANK()`, `LAG()/LEAD()` — [SQL Manual → 3.1](manual_consultas_sql.md#31-window-functions-rango-y-agregación)
- **CTE Recursivas:** Grafos, rutas conectadas — [Manual SQL → 2.2](manual_consultas_sql.md#22-recorrido-de-grafos-rutas-conectadas)
- **SCD Tipo 2:** Dimensiones cambiantes lentamente — [Doc M2 → 6.2.2](PI_M2_DOCUMENTATION_DODY.md#622-dimensión-vehículo-scd-tipo-2)

###高級 (Advanced)
- **PostgreSQL Tuning:** `EXPLAIN ANALYZE`, índices BRIN/partial — [Doc M2 → 4.2](PI_M2_DOCUMENTATION_DODY.md#42-explain-analyze-en-acción)
- **Vectorización:** Eliminación de bucles `for` — [Doc M2 → 5.1](PI_M2_DOCUMENTATION_DODY.md#51-arquitectura-del-pipeline)
- **Serverless Patterns:** Cold start mitigation, scaling — [Arquitectura → 8](arquitectura_tecnica.md#8-diseño-resiliente-serverless-aws-amazon-web-services)

---

## 🎯 Tutoriales Paso a Paso

### Para Desarrolladores Nuevos

1. **Primeros 5 minutos**
   - [Setup local con Docker](../dashboard/setup/README.md)
   - [Generar datos sintéticos](setup_guide.md#3-generar-datos-sintéticos)
   - [Lanzar dashboard](setup_guide.md#7-lanzar-dashboard)

2. **Primera query analítica**
   - [Conectarse a PostgreSQL](manual_consultas_sql.md#1-conexión-y-configuración)
   - [Ejecutar KPI simple](manual_consultas_sql.md#11-kpi-tasa-de-entregas-a-tiempo)
   - [Optimizar con índices](manual_consultas_sql.md#41-creación-de-índices-recomendados)

3. **Primera función Lambda**
   - [Plantilla base](../lambda_functions/eta_calculator.py)
   - [Desplegar con SAM](setup_guide.md#6-desplegar-aws-local)
   - [Probar endpoint](arquitectura_tecnica.md#31-monitoreo-estratégico)

---

## 📊 Tableros de Referencia

### Tabla: Índices PostgreSQL Recomendados
| Tabla | Índice | Uso | Mejora |
|-------|--------|-----|--------|
| `deliveries` | `idx_deliveries_status` (partial) | Filtros por estado | **450x** |
| `trips` | `idx_trips_multi` (compuesto) | Búsquedas multidimensionales | **120x** |
| `routes` | `idx_routes_distance_brin` (BRIN) | Series temporales | **80x** |

### Tabla: Costos AWS (200 vehículos)
| Servicio | Free Tier | Post-Free | Optimizado |
|----------|-----------|-----------|------------|
| Lambda | 1M req/mes gratis | $0.20/millón | < $5/mes |
| S3 | 5GB gratis | $0.023/GB | < $10/mes |
| RDS | 750h/mes t2.micro | $30/mes | $30/mes |
| **Total** | **Cobertura 80%** | **~$45/mes** | **< $45/mes** |

---

## ❓ FAQ

**¿Cómo escalar a +1M de registros?**
→ Usar particionamiento por rango en `departure_datetime` + índices BRIN. Ver [Doc M2 → 4.4](PI_M2_DOCUMENTATION_DODY.md#44-configuración-de-rendimiento).

**¿Snowflake vs Redshift?**
→ Snowflake: separación cómputo/almacenamiento, pricing por segundo, mejor para datos semiestructurados. Comparación en [Doc M2 → 6.1](PI_M2_DOCUMENTATION_DODY.md#61-arquitectura-de-snowflake).

**¿PostgREST vs FastAPI?**
→ PostgREST: cero código, permisos granulares via PG roles. FastAPI: lógica custom. Ver [Doc M2 → 10](PI_M2_DOCUMENTATION_DODY.md#10-postgrest-api-rest-automática).

**¿Cómo obtener datos reales en producción?**
→ Reemplazar generador sintético por:
- API REST de partner logístico (OAuth2)
- Kafka/Kinesis para streaming
- S3 buckets con archivos CSV diarios

---

## 📞 Soporte y Contacto

**Autor:** Dody Dueñas  
📧 Email: dody.duenas@example.com  
🔗 [LinkedIn](https://linkedin.com/in/dodyduenas)  
🐙 [GitHub](https://github.com/dodyduenas)

Para consultas técnicas sobre:
- **Pipeline ETL:** Ver [Doc M2 → Sección 5](PI_M2_DOCUMENTATION_DODY.md#5-técnicas-de-integración-etl--elt-con-python)
- **AWS:** Revisar [arquitectura técnica](arquitectura_tecnica.md)
- **SQL:** Consultar [manual de queries](manual_consultas_sql.md)

---

## 🏆 Reconocimientos

- **Henry Data Science** — Programa Full Stack Data Science (M2, 2026)
- **Comisión Técnica M2** — Por su exigencia y retroalimentación
- **Compañeros de Cohort** — Por el código abierto y colaborativo

---

*Última actualización: Abril 2026*  
*FleetLogix Master · Enterprise Data Science Platform · Nivel Senior*

---

### 🧭 Navegación de Documentos

⬅️ Anterior: [README Principal](../README.md)  
🔝 Arriba: [Volver al inicio](#-documentación-fleetlogix-master)  
⬇️ Siguiente: [Arquitectura Técnica →](arquitectura_tecnica.md)
