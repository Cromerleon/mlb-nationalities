# ⚾ MLB Nacionalidades

Proyecto de datos que extrae, almacena y visualiza información de los jugadores activos de MLB según su país de nacimiento. Los datos se actualizan automáticamente todos los días mediante GitHub Actions, sin intervención manual.

**Dashboard en vivo:** [agregar aquí el link de Streamlit Community Cloud]

---

## 📋 Descripción

Este proyecto responde a la pregunta: *¿cómo está compuesta MLB en términos de nacionalidad de sus jugadores, y cómo cambia esa composición con el tiempo?*

Cada día, un pipeline automatizado:
1. Consulta la MLB Stats API para traer los 26-man rosters de los 30 equipos
2. Actualiza una base de datos SQLite con el estado actual de cada jugador
3. Guarda un snapshot histórico agregado por país, para poder analizar tendencias en el tiempo
4. Publica los cambios en este repositorio

Un dashboard en Streamlit consume esos datos y permite explorar la información de forma interactiva.

---

## 🛠️ Stack técnico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.14 |
| Fuente de datos | [MLB Stats API](https://statsapi.mlb.com) vía librería `MLB-StatsAPI` |
| Base de datos | SQLite |
| Análisis | pandas |
| Visualización | Streamlit |
| Automatización local | Windows Task Scheduler |
| Automatización en la nube | GitHub Actions |
| Despliegue | Streamlit Community Cloud |

---

## 🗂️ Estructura del repositorio

```
mlb-nacionalidades/
├── .github/workflows/
│   └── actualizar.yml       # Workflow de GitHub Actions (corre a las 4am hora local)
├── exploracion.ipynb         # Notebook de aprendizaje y desarrollo (proceso, con prueba y error)
├── analisis.ipynb            # Notebook limpio con el análisis final
├── extract_daily.py          # Script de extracción y carga (usado por la automatización)
├── app.py                    # Dashboard de Streamlit
├── mlb_nacionalidades.db     # Base de datos SQLite (se actualiza sola cada día)
├── requirements.txt
└── README.md
```

---

## 🗃️ Modelo de datos

### Tabla `jugadores`
Foto actual de cada jugador activo (una fila por `player_id`, se actualiza por *upsert*).

| Campo | Tipo | Descripción |
|---|---|---|
| `player_id` | INTEGER (PK) | ID único del jugador según la API |
| `nombre` | TEXT | Nombre completo |
| `pais_nacimiento` | TEXT | País de nacimiento |
| `ciudad_nacimiento` | TEXT | Ciudad de nacimiento |
| `anio_debut` | INTEGER | Año de debut en MLB |
| `equipo_id` / `equipo_nombre` | INTEGER / TEXT | Equipo actual |
| `posicion` | TEXT | Posición de juego |
| `activo` | BOOLEAN | Estado activo según la API |
| `fecha_actualizacion` | TEXT | Última vez que se actualizó este registro |

### Tabla `historial_diario`
Bitácora acumulativa: conteo de jugadores por país, una "foto" nueva cada día (no se sobreescribe).

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER (PK autoincremental) | Identificador de fila |
| `fecha` | TEXT | Fecha del snapshot |
| `pais_nacimiento` | TEXT | País |
| `cantidad_jugadores` | INTEGER | Cantidad de jugadores activos de ese país ese día |

---

## 🔄 Automatización

- **GitHub Actions** (`actualizar.yml`): corre todos los días a las 8:00 UTC (4:00am hora de RD). Instala dependencias, ejecuta `extract_daily.py`, y hace commit/push automático de la base de datos actualizada.
- **Windows Task Scheduler**: se usó como ejercicio de aprendizaje para correr el script localmente. Actualmente desactivado a favor de GitHub Actions, que no depende de que la PC esté encendida.

---

## 📊 Dashboard

La app de Streamlit (`app.py`) tiene dos secciones:

- **Menú Principal**: totales generales y tabla ordenable de jugadores por país
- **Datos por Nacionalidad**: selector de equipo + tabla de países con esa organización; al hacer click en un país se despliega el listado de jugadores (nombre, posición, ciudad, año de debut)

---

## 🚀 Cómo correrlo localmente

```bash
git clone https://github.com/Cromerleon/mlb-nacionalidades.git
cd mlb-nacionalidades
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Extraer datos frescos (opcional, ya viene una copia de la base de datos en el repo)
python extract_daily.py

# Correr el dashboard
streamlit run app.py
```

---

## 🗺️ Roadmap

### Tabla `estadisticas` (pendiente)

Actualmente el proyecto guarda datos biográficos y de roster, pero no estadísticas de rendimiento (bateo/pitcheo). Se decidió posponer esto deliberadamente en la fase de diseño, para no sobrecargar las primeras fases del proyecto.

**Diseño planeado:**

Una tabla separada de `jugadores`, porque las estadísticas dependen de la temporada y del tipo de jugador (bateador vs. pitcher tienen métricas distintas):

| Campo | Tipo | Notas |
|---|---|---|
| `id` | INTEGER (PK autoincremental) | |
| `player_id` | INTEGER (FK → jugadores) | |
| `temporada` | INTEGER | Año de la temporada |
| `tipo` | TEXT | `'bateo'` o `'pitcheo'` |
| *(columnas de métricas)* | REAL/INTEGER | Ej. bateo: AVG, HR, RBI, OPS · pitcheo: ERA, WHIP, K, IP |
| `fecha_actualizacion` | TEXT | |

Esto permite tener **varias filas por jugador** (una por temporada), sin dejar columnas vacías para quienes no aplican (un pitcher no tiene AVG relevante, un bateador no tiene ERA).

**Pasos previstos para implementarlo:**
1. Explorar el endpoint de estadísticas de la MLB Stats API (`person` con `hydrate=stats`, o el endpoint dedicado de stats por jugador/temporada)
2. Definir qué métricas concretas se van a guardar para cada tipo
3. Crear la tabla y su función de carga (`obtener_stats_jugador`, `guardar_estadisticas`)
4. Integrar la carga de stats al flujo diario de `extract_daily.py`
5. Agregar una sección al dashboard con líderes estadísticos, filtrable por país de nacimiento (ej. "líderes de bateo entre jugadores dominicanos")

### Otras mejoras futuras
- Posible expansión a jugadores en ligas menores o prospectos

---
