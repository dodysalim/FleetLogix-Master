# 🤖 Guía para Agentes (Kiloyotros AI Coding Assistants)

Este archivo contiene instrucciones específicas para trabajar con el proyecto **FleetLogix Master**. Todo agente que intervenga en el codebase debe leer este archivo primero.

---

## 📋 Identificación del Proyecto

| Campo | Valor |
|-------|-------|
| **Nombre** | FleetLogix Master — Plataforma Empresarial de Ciencia de Datos |
| **Versión** | 1.0.0 (Producción) |
| **Autor** | Dody Dueñas (Henry Data Science M2) |
| **Tipo** | Data Engineering + Data Science + Cloud-native |
| **Estado** | Production Ready ✅ |

---

## 🏗️ Arquitectura General (Resumen)

```
[PostgreSQL OLTP] → [ETL Pipeline (Python)] → [Snowflake Star Schema]
       ↓                                      ↓
[AWS Lambda] ← [IoT/MongoDB]          [PostgREST API]
                                           ↓
                                   [Streamlit Dashboard]
```

**Capas:**
1. **Ingestión:** PostgreSQL (transaccional) + Synthetic Data Generator
2. **Procesamiento:** ETL con Pandas vectorizado, chunking 100K
3. **Almacenamiento:** Snowflake (DW) + S3 (lake) + DynamoDB (real-time)
4. **Servicios:** PostgREST (REST API) + Streamlit (BI)
5. **Cloud:** AWS Lambda serverless + CloudWatch monitoring

---

## 📂 Estructura de Directorios (Patrones)

```
Proyecto2Dody/
├── 📂 scripts/                # ETL, generadores, utils
│   ├── generate_synthetic_data.py   # ↓ 500K+ registros
│   ├── load_to_postgres.py          # → PostgreSQL
│   └── etl_to_snowflake.py          # → Snowflake
├── 📂 sql/                    # Queries DDL/DML
│   ├── schema.sql                    # Tablas PG
│   ├── queries.sql                   # 12 queries analíticas
│   ├── snowflake_schema.sql          # DDL Star Schema
│   └── optimization_indexes.sql      # Índices optimizados
├── 📂 lambda_functions/       # AWS Lambda
│   ├── eta_calculator.py
│   ├── deviation_detector.py
│   └── daily_reporter.py
├── 📂 dashboard/              # Streamlit app
│   ├── app.py                        # Entrada principal
│   ├── pages/                        # Páginas adicionales
│   └── data_exports/                 # CSV/JSON exports
├── 📂 docs/                   # Documentación técnica
│   ├── INDEX.md                      # 🧭 Navegación principal
│   ├── PI_M2_DOCUMENTATION_DODY.md   # 📘 Manual exhaustivo (1,378 líneas)
│   ├── arquitectura_tecnica.md       # ☁️ AWS + IoT (1,447 líneas)
│   ├── setup_guide.md               # 🛠️ Instalación paso a paso
│   ├── diccionario_de_datos.md       # 📊 Diccionario de datos
│   ├── manual_consultas_sql.md       # 💾 50+ queries
│   └── evidencia_ejecucion/          # 📸 Capturas + logs
├── 📂 docker/                # Configuración contenedores
│   ├── docker-compose.yml
│   ├── postgres/
│   ├── postgrest/
│   └── streamlit/
├── 📄 README.md              # 📖 Documentación principal (NUEVO)
├── 📄 kilo.json              # ⚙️ Configuración del proyecto
└── 📄 AGENTS.md              # 🤖 Este archivo
```

---

## 🎯 Convenciones de Código

### Python
- **Formato:** Black (line length 88)
- **Linter:** Ruff (pep8, flake8, isort combined)
- **Type hints:** Obligatorios en funciones públicas
- **Docstrings:** Google Style (triple comillas dobles)

```python
def calculate_eta(route_id: int, departure: datetime) -> dict:
    """Calcula tiempo estimado de arribo basado en ruta y condiciones.
    
    Args:
        route_id: ID de la ruta programada
        departure: Fecha/hora de salida programada
        
    Returns:
        dict: {eta: datetime, confidence: float, factors: list}
        
    Raises:
        ValueError: Si route_id no existe
    """
    ...
```

### SQL
- **Indentación:** 4 espacios (no tabs)
- **Mayúsculas:** Palabras clave SQL en MAYÚSCULAS
- **Aliases:** snake_case, cortos pero descriptivos
- **Comentarios:** -- en línea separada arriba de la sentencia

```sql
-- Calcular tasa de entregas a tiempo por mes
SELECT 
    d.year,
    d.month_name,
    COUNT(*) AS total_deliveries,
    SUM(CASE WHEN fd.delay_minutes <= 0 THEN 1 ELSE 0 END) AS on_time_count,
    ROUND(100.0 * SUM(CASE WHEN fd.delay_minutes <= 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS on_time_pct
FROM fact_deliveries fd
JOIN dim_date d ON fd.date_key = d.date_key
GROUP BY d.year, d.month_num, d.month_name
ORDER BY d.year DESC, d.month_num DESC;
```

### Docker
- **Imágenes:** Usar Alpine cuando sea posible
- **Volúmenes:** Named volumes para datos persistentes
- **Redes:** Bridge network por defecto
- **Healthchecks:** SIEMPRE incluir

```dockerfile
FROM postgres:15-alpine
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}
```

### Commits
- **Formato:** Conventional Commits
- **Lenguaje:** Inglés (código) / Español (mensajes de commit permitidos)
- **Prefijos:** `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

```
feat: agregar módulo de detección de desvíos en AWS Lambda
fix: corregir bug en cálculo ETA para rutas con tráfico
docs: actualizar README con nueva arquitectura
refactor: optimizar ETL pipeline usando vectorización
test: agregar unit tests para etl_to_snowflake.py
```

---

## 🔑 Variables de Entorno Críticas

| Variable | Requerida | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `POSTGRES_PASSWORD` | ✅ SI | Contraseña admin PostgreSQL | `ChangeMe_2026!` |
| `PGRST_JWT_SECRET` | ✅ SI | Secreto JWT para API | `jwt_secret_32chars_min` |
| `SNOWFLAKE_ACCOUNT` | ❌ No | Solo producción | `tcucrelq-kb28178` |
| `AWS_ACCESS_KEY_ID` | ❌ No | Solo Lambda/S3 | `AKIAIOSFODNN7...` |
| `LOG_LEVEL` | ❌ No | Nivel de logs | `INFO` / `DEBUG` |

> **⚠️ Nunca committear `.env`** — ya está en `.gitignore`.

---

## 🧪 Testing y Calidad

### Comandos de Calidad

```bash
# Instalar dependencias dev
pip install -e ".[dev]"

# Linting (ruff + black check)
make lint

# Auto-formateo (black)
make format

# Type checking (mypy)
make typecheck

# Unit tests (pytest)
make test
make test-coverage  # → HTML report en htmlcov/

# Todo en uno (CI)
make ci-check
```

### Cobertura Mínima
- **Core modules:** 90%
- **ETL pipeline:** 85%
- **Lambda functions:** 80%
- **Dashboard:** 70%

---

## 📊 Datos de Referencia

### Tamaños de Tablas (Esperados)

| Tabla | Registros | Descripción |
|-------|-----------|-------------|
| `vehicles` | ~200 | Flota activa |
| `drivers` | ~400 | Conductores registrados |
| `routes` | ~50 | Rutas frecuentes |
| `trips` | ~100,000 | Viajes programados |
| `deliveries` | ~400,000 | Entregas (detalle) |
| `maintenance` | ~5,000 | Registros de mantención |
| **Total** | **~505,650** | **Registros sintéticos** |

### Esquema Star (Snowflake)

```
               fact_deliveries (500K)
                      |
        +-------------+-------------+-------------+-------------+
        ↓             ↓             ↓             ↓             ↓
 dim_date(365) dim_vehicle(200) dim_driver(400) dim_route(50) dim_customer(1K)
```

---

## 🔍 Checklist Antes de Commit

```markdown
- [ ] Código formateado con Black (`make format`)
- [ ] Sin errores de lint (`make lint` → 0 errores)
- [ ] Type hints completos (mypy OK)
- [ ] Tests nuevos añadidos (coverage no decrece)
- [ ] Docstrings actualizados (Google Style)
- [ ] No hardcodeado secrets (usar os.getenv())
- [ ] SQL validado (EXPLAIN ANALYZE si es query compleja)
- [ ] README actualizado si cambia UX/API pública
- [ ] Migraciones documentadas si hay schema change
```

---

## 🚀 Comandos Rápidos (Cheatsheet)

```bash
# Setup inicial (una sola vez)
docker compose up -d && cp .env.example .env && code .env

# Desarrollo diario
make lint && make test && git status

# Generar más datos
python scripts/generate_synthetic_data.py --records 100000 --append True

# Ver queries lentas
psql -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Debug Lambda local
sam local invoke ETAcalculator -e events/eta_event.json

# Dashboard en producción
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0

# Respaldo Snowflake
snowsql -q "COPY INTO @stage/backup/ FROM fact_deliveries FILE_FORMAT = (TYPE=CSV)"

# Monitoreo CloudWatch (local)
aws logs tail /aws/lambda/eta-calculator --follow
```

---

## 📖 Documentación Importante

Lee en orden:

1. **[README.md](../README.md)** — Visión general + quickstart
2. **[docs/SETUP_GUIDE.md](SETUP_GUIDE.md)** — Instalación detallada
3. **[docs/PI_M2_DOCUMENTATION_DODY.md](PI_M2_DOCUMENTATION_DODY.md)** — Manual técnico completo
4. **[docs/arquitectura_tecnica.md](arquitectura_tecnica.md)** — AWS + IoT
5. **[docs/manual_consultas_sql.md](manual_consultas_sql.md)** — SQL optimization
6. **[dashboard/KPIs.md](../dashboard/KPIs.md)** — Métricas de negocio

---

## 🐛 Debugging Tips

| Síntoma | Diagnóstico | Solución |
|---------|-------------|----------|
| ETL lento (>2min) | `EXPLAIN ANALYZE` en queries | Crear índices → [ver doc 4.2](PI_M2_DOCUMENTATION_DODY.md#42-explain-analyze-en-acción) |
| API 500 error | Revisar logs Lambda | `sam local logs -n FunctionName` |
| Dashboard carga lento | Cache de Streamlit | `rm -rf ~/.streamlit/` |
| Docker OOM | Chunksize muy grande | Reducir `--chunk-size 50000` |
| Snowflake query lento | Warehousetoo small | `ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = 'LARGE';` |

---

## 🏆 Estándares de Calidad (M2 Henry)

| Criterio | Mínimo | Objetivo | Estado Actual |
|----------|--------|----------|---------------|
| **Registros generados** | +500K | +505K | ✅ 505,650 |
| **Tablas relacionadas** | 6 | 6 | ✅ |
| **Queries analíticas** | 12 | 15+ | ✅ |
| **Queries optimizadas** | 3 | 5+ | ✅ (450x mejora) |
| **Índices creados** | 5 | 8+ | ✅ |
| **Documentación** | 10 páginas | 20+ páginas | ✅ (3,500+ líneas) |
| **Dashboard funcional** | Sí | Sí + Streamlit | ✅ |
| **API REST** | Opcional | PostgREST | ✅ |
| **Cloud (AWS)** | Opcional | Lambda + S3 | ✅ |
| **Cobertura tests** | 0% | 80%+ | ⚠️ 85%+ |

---

## 🎓 Recursos de Aprendizaje

### SQL Avanzado
- [PostgreSQL Docs](https://www.postgresql.org/docs/current/)
- [Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)
- [CTE Recursivas](https://www.postgresql.org/docs/current/queries-with.html)

### Data Modeling
- [Kimball Group](https://www.kimballgroup.com/) — Dimensional Modeling
- [Inmon](https://www.inmon.com/) — Corporate Information Factory

### AWS Serverless
- [Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)
- [Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

### Streamlit
- [Streamlit Docs](https://docs.streamlit.io/)
- [Component Gallery](https://streamlit.io/components)

---

## 🔄 Flujo de Trabajo Recomendado

```bash
# 1. Pick issue/task from GitHub Projects
git checkout -b feature/<short-desc>-<issue-number>

# 2. Develop with tests
make test  # correr tests cada ~15 min

# 3. Lint & format
make lint && make format

# 4. Commit ( Conventional Commits )
git add .
git commit -m "feat: agregar detector de desvíos en Lambda"

# 5. Push + PR
git push -u origin feature/<branch>
# Abrir PR en GitHub, asignar reviewer
```

**Branch naming:**
- `feat/nueva-functionality` — nueva feature
- `fix/bug-description` — bug fix
- `docs/update-section` — documentación
- `refactor/restructure-code` — refactor sin cambio funcional
- `test/add-coverage` — añadir tests

---

## 📞 Contacto y Soporte

**Autor Principal:** Dody Dueñas  
📧 dody.duenas@example.com  
🐙 [GitHub](https://github.com/dodyduenas)  
💼 [LinkedIn](https://linkedin.com/in/dodyduenas)

---

## 📜 Licencia

MIT License — Ver [`LICENSE`](../LICENSE) para detalles.

---

*Última actualización: Abril 2026*  
*FleetLogix Master — Enterprise Data Science Platform*

---

**🚀 Comienza aquí:** [README.md](../README.md) → [Setup Guide](SETUP_GUIDE.md) → [Documentación Técnica](PI_M2_DOCUMENTATION_DODY.md)
