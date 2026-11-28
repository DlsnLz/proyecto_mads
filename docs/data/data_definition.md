# Definición de los datos

## Origen de los datos

* **Fuente primaria:** New York City Taxi and Limousine Commission (NYC TLC) — *TLC Trip Record Data* (registros públicos de viajes de taxis verdes / *Street-Hail Livery - SHL*).
* **Portal oficial de obtención:** [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page), complementado con el catálogo geográfico oficial *Taxi Zone Lookup Table*.
* **Cobertura temporal:** Primer semestre de 2024 (**enero a junio de 2024**, 6 particiones mensuales) con un volumen total de **339,807 registros crudos** y **265 zonas geográficas** catalogadas.
* **Método de obtención y versionamiento:** Los archivos originales en formato columna binario (`.parquet`) y el catálogo de zonas (`.csv`) fueron descargados desde el portal oficial de la TLC y registrados mediante **DVC (Data Version Control)** utilizando un almacenamiento remoto en **Google Drive**, garantizando reproducibilidad sin almacenar archivos pesados directamente en Git.

---

## Especificación de los scripts para la carga de datos

La ingesta, validación de esquema, limpieza inicial y generación del dataset consolidado se gestionan estrictamente mediante la estructura modular del repositorio:

* **`scripts/data_acquisition/main.py`**: Script orquestador encargado de verificar la disponibilidad de los insumos descargados mediante `dvc pull` en `data/raw/` y auditar el esquema físico, tipos de datos y conteo de nulos de los 6 archivos mensuales.
* **`scripts/preprocessing/main.py`**: Script encargado de ejecutar la limpieza, cálculo de la variable objetivo (`duration_min`), filtrado de anomalías, enriquecimiento geográfico y exportación del conjunto procesado en `data/processed/` (**315,128 registros válidos**, `92.74%` de retención).
* **`src/nombre_paquete/database/loader.py`**: Módulo reutilizable con funciones para carga eficiente de archivos `.parquet`, lectura del catálogo `taxi_zone_lookup.csv` y extracción de metadatos de esquema.
* **`src/nombre_paquete/preprocessing/cleaning.py`**: Módulo que implementa las reglas deterministas de filtrado, imputación controlada y prevención de *data leakage*.

---

## Referencias a rutas o bases de datos origen y destino

El flujo de datos sigue una arquitectura local respaldada por control de versiones de datos (DVC):

* **Almacenamiento remoto (DVC Remote):** Carpeta institucional en Google Drive vinculada en `.dvc/config` y rastreada por `data/raw.dvc`.
* **Ruta de origen local:** `data/raw/`
* **Ruta de destino local:** `data/processed/`

### Rutas de origen de datos

#### 1. Ubicación de los archivos de origen
Todos los insumos crudos residen en el directorio `data/raw/` (gestionado por DVC):
* `data/raw/green_tripdata_2024-01.parquet`
* `data/raw/green_tripdata_2024-02.parquet`
* `data/raw/green_tripdata_2024-03.parquet`
* `data/raw/green_tripdata_2024-04.parquet`
* `data/raw/green_tripdata_2024-05.parquet`
* `data/raw/green_tripdata_2024-06.parquet`
* `data/raw/taxi_zone_lookup.csv`

#### 2. Estructura de los archivos de origen

**A. Registros de viajes (`green_tripdata_2024-01.parquet` a `2024-06.parquet`) — 339,807 filas × 20 columnas:**

| Columna | Tipo verificado | Nulos (%) | Descripción breve |
| :--- | :--- | :--- | :--- |
| `VendorID` | `int32` | 0.00% | Código del proveedor tecnológico LPEP (`1` = CMT, `2` = VeriFone). |
| `lpep_pickup_datetime` | `datetime64[us]` | 0.00% | Fecha y hora de activación del taxímetro (inicio del viaje). |
| `lpep_dropoff_datetime` | `datetime64[us]` | 0.00% | Fecha y hora de desactivación del taxímetro (fin del viaje). |
| `store_and_fwd_flag` | `str` | 4.18% | Indicador de almacenamiento temporal antes de envío (`Y` / `N`). |
| `RatecodeID` | `float64` | 4.18% | Código de tarifa aplicada (`1` a `6`, `99` = Nulo). |
| `PULocationID` | `int32` | 0.00% | Identificador de zona TLC de origen (*Pickup*). |
| `DOLocationID` | `int32` | 0.00% | Identificador de zona TLC de destino (*Dropoff*). |
| `passenger_count` | `float64` | 4.18% | Número de pasajeros reportado por el conductor. |
| `trip_distance` | `float64` | 0.00% | Distancia recorrida reportada por el taxímetro (en millas). |
| `fare_amount` | `float64` | 0.00% | Tarifa base calculada por tiempo y distancia (USD). |
| `extra` | `float64` | 0.00% | Recargos adicionales por hora pico o nocturna (USD). |
| `mta_tax` | `float64` | 0.00% | Impuesto fijo de la MTA (USD). |
| `tip_amount` | `float64` | 0.00% | Propina registrada en pagos con tarjeta (USD). |
| `tolls_amount` | `float64` | 0.00% | Total de peajes pagados en el trayecto (USD). |
| `ehail_fee` | `float64` | 100.00% | Cargo por solicitud electrónica (completamente nulo en el dataset). |
| `improvement_surcharge` | `float64` | 0.00% | Recargo de mejora de infraestructura (USD). |
| `total_amount` | `float64` | 0.00% | Monto total cobrado al pasajero (USD). |
| `payment_type` | `float64` | 4.18% | Método de pago (`1` = Tarjeta, `2` = Efectivo, etc.). |
| `trip_type` | `float64` | 4.20% | Tipo de despacho (`1` = Street-hail, `2` = Dispatch). |
| `congestion_surcharge` | `float64` | 4.18% | Recargo por congestión en Manhattan (USD). |

**B. Catálogo de zonas (`taxi_zone_lookup.csv`) — 265 filas × 4 columnas:**

| Columna | Tipo de dato | Descripción breve |
| :--- | :--- | :--- |
| `LocationID` | `int64` | Llave primaria de la zona TLC (`1` a `265`), enlazable con `PULocationID` y `DOLocationID`. |
| `Borough` | `string` | Distrito (*borough*) de NYC (`Manhattan`, `Brooklyn`, `Queens`, `Bronx`, `Staten Island`, `EWR`). |
| `Zone` | `string` | Nombre específico del barrio o zona operativa TLC. |
| `service_zone` | `string` | Categoría de zona de servicio (`Yellow Zone`, `Boro Zone`, `Airports`, `EWR`). |

#### 3. Procedimientos de transformación y limpieza en origen
1. **Unificación temporal:** Concatenación vertical de las 6 tablas mensuales y filtrado estricto al intervalo `2024-01-01 00:00:00` $\le$ `lpep_pickup_datetime` $<$ `2024-07-01 00:00:00`.
2. **Cálculo de la variable objetivo (`duration_min`):**
   $$\text{duration\_min} = \frac{\text{lpep\_dropoff\_datetime} - \text{lpep\_pickup\_datetime}}{60}$$
3. **Filtrado de calidad e integridad (reteniendo 315,128 de 339,807 registros — 92.74%):**
   * Exclusión de viajes con duración no válida o extrema ($\text{duration\_min} \le 1\text{ min}$ o $\text{duration\_min} > 180\text{ min}$).
   * Exclusión de distancias inconsistentes ($\text{trip\_distance} \le 0\text{ millas}$ o $\text{trip\_distance} > 100\text{ millas}$).
   * Exclusión de códigos de zona nulos o fuera del catálogo válido (`PULocationID` o `DOLocationID` nulos o en `{264, 265}`).
4. **Prevención de fuga de información (*Data Leakage*):** Descarte de variables post-viaje (`lpep_dropoff_datetime`, `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `payment_type`, `congestion_surcharge`, `ehail_fee`).

---

### Base de datos de destino

#### 1. Ubicación de destino
La salida consolidada y limpia se almacena como archivo columnar en:
* **Archivo maestro limpio:** `data/processed/green_trips_2024_h1_clean.parquet` (`315,128` filas × `13` columnas).

#### 2. Estructura de la tabla de destino (`green_trips_2024_h1_clean.parquet`)

| Columna | Tipo de dato | Rol en el modelo | Descripción |
| :--- | :--- | :--- | :--- |
| `duration_min` | `float64` | **Target ($y$)** | Duración real del viaje en minutos. |
| `PULocationID` | `int32` | Feature categórica | ID de zona TLC de origen (entrada para capa *Embedding*). |
| `DOLocationID` | `int32` | Feature categórica | ID de zona TLC de destino (entrada para capa *Embedding*). |
| `PU_Borough` | `string` | Feature categórica | Distrito de origen enriquecido desde `taxi_zone_lookup.csv`. |
| `DO_Borough` | `string` | Feature categórica | Distrito de destino enriquecido desde `taxi_zone_lookup.csv`. |
| `trip_distance` | `float64` | Feature numérica | Distancia recorrida del trayecto en millas. |
| `pickup_hour` | `int8` | Feature temporal | Hora del día del inicio del viaje (`0` a `23`). |
| `pickup_dayofweek` | `int8` | Feature temporal | Día de la semana (`0` = Lunes a `6` = Domingo). |
| `is_weekend` | `int8` | Feature temporal | Indicador binario de fin de semana (`1` si sábado/domingo, `0` si no). |
| `pickup_month` | `int8` | Feature temporal | Mes del viaje (`1` a `6` para partición temporal *train/val/test*). |
| `RatecodeID` | `int8` | Feature categórica | Código de tarifa inicial imputado (`1` en nulos). |
| `VendorID` | `int8` | Feature categórica | Proveedor del sistema LPEP (`1` o `2`). |
| `passenger_count` | `float32` | Feature numérica | Cantidad de pasajeros (imputada con mediana en valores nulos). |

#### 3. Procedimientos de carga y transformación en destino
1. **Enriquecimiento geográfico:** Unión (*left join*) de `PULocationID` y `DOLocationID` contra `taxi_zone_lookup.csv` para anexar `PU_Borough` y `DO_Borough`.
2. **Ingeniería de características temporales:** Extracción de `pickup_hour`, `pickup_dayofweek`, `is_weekend` y `pickup_month` a partir de `lpep_pickup_datetime`.
3. **Imputación controlada:** Imputación determinista de los `14,219` registros con valores faltantes en `passenger_count` (mediana) y `RatecodeID` (código estándar `1`).
4. **Serialización optimizada:** Compresión en formato `.parquet` (`snappy`) en `data/processed/green_trips_2024_h1_clean.parquet`.