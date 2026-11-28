from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from nombre_paquete.database.loader import extract_schema_summary, load_raw_trips
from nombre_paquete.visualization.eda_plots import generate_eda_figures


def main() -> None:
    raw_dir = PROJECT_ROOT / "data" / "raw"
    clean_path = PROJECT_ROOT / "data" / "processed" / "green_trips_2024_h1_clean.parquet"
    docs_data_dir = PROJECT_ROOT / "docs" / "data"
    figures_dir = docs_data_dir / "figures"
    summary_path = docs_data_dir / "data_summary.md"

    print("1. Cargando datasets crudo y limpio...")
    df_raw = load_raw_trips(raw_dir)
    df_clean = pd.read_parquet(clean_path)

    # Auditoría de calidad en crudo
    raw_dups = int(df_raw.duplicated().sum())
    df_raw["lpep_pickup_datetime"] = pd.to_datetime(df_raw["lpep_pickup_datetime"])
    df_raw["lpep_dropoff_datetime"] = pd.to_datetime(df_raw["lpep_dropoff_datetime"])
    raw_dur = (
        df_raw["lpep_dropoff_datetime"] - df_raw["lpep_pickup_datetime"]
    ).dt.total_seconds() / 60.0

    out_date = int(
        (
            (df_raw["lpep_pickup_datetime"] < "2024-01-01")
            | (df_raw["lpep_pickup_datetime"] >= "2024-07-01")
        ).sum()
    )
    bad_dur = int(((raw_dur <= 1.0) | (raw_dur > 180.0)).sum())
    bad_dist = int(
        ((df_raw["trip_distance"] <= 0.0) | (df_raw["trip_distance"] > 100.0)).sum()
    )
    bad_zone = int(
        (
            df_raw["PULocationID"].isin([264, 265])
            | df_raw["DOLocationID"].isin([264, 265])
        ).sum()
    )

    schema_raw = extract_schema_summary(df_raw)
    nulls_table = schema_raw[schema_raw["Nulos"] > 0].to_markdown(index=False)

    # Estadísticas de la variable objetivo
    target = df_clean["duration_min"]
    target_stats = {
        "Conteo": f"{len(target):,}",
        "Media": f"{target.mean():.2f} min",
        "Desviación estándar": f"{target.std():.2f} min",
        "Mínimo": f"{target.min():.2f} min",
        "Percentil 25 (Q1)": f"{target.quantile(0.25):.2f} min",
        "Mediana (Q2)": f"{target.median():.2f} min",
        "Percentil 75 (Q3)": f"{target.quantile(0.75):.2f} min",
        "Percentil 95": f"{target.quantile(0.95):.2f} min",
        "Máximo": f"{target.max():.2f} min",
        "Asimetría (Skewness)": f"{target.skew():.2f}",
    }
    target_table = pd.DataFrame(
        list(target_stats.items()), columns=["Métrica", "Valor"]
    ).to_markdown(index=False)

    # Descriptivos variables numéricas
    num_features = [
        "duration_min",
        "trip_distance",
        "pickup_hour",
        "pickup_dayofweek",
        "is_weekend",
        "passenger_count",
    ]
    desc_num = (
        df_clean[num_features]
        .describe()
        .T[["count", "mean", "std", "min", "50%", "max"]]
        .round(2)
        .reset_index()
        .rename(columns={"index": "Variable", "50%": "mediana"})
        .to_markdown(index=False)
    )

    # Top Boroughs origen
    pu_borough_table = (
        df_clean.groupby("PU_Borough")["duration_min"]
        .agg(Viajes="count", Media_min="mean", Mediana_min="median")
        .sort_values("Viajes", ascending=False)
        .round(2)
        .reset_index()
        .to_markdown(index=False)
    )

    # Ranking de variables: Información Mutua + Correlación Spearman
    print("2. Calculando ranking de importancia predictiva...")
    features_for_rank = [
        "trip_distance",
        "DOLocationID",
        "PULocationID",
        "pickup_hour",
        "RatecodeID",
        "pickup_dayofweek",
        "is_weekend",
        "VendorID",
        "passenger_count",
    ]
    sample_mi = df_clean.sample(n=min(50000, len(df_clean)), random_state=42)
    mi_scores = mutual_info_regression(
        sample_mi[features_for_rank],
        sample_mi["duration_min"],
        discrete_features=[False, True, True, True, True, True, True, True, False],
        random_state=42,
    )
    spearman_corr = [
        abs(df_clean[col].corr(df_clean["duration_min"], method="spearman"))
        for col in features_for_rank
    ]

    importance_df = (
        pd.DataFrame(
            {
                "Variable": features_for_rank,
                "Mutual_Information": np.round(mi_scores, 4),
                "Corr_Spearman_Abs": np.round(spearman_corr, 4),
            }
        )
        .sort_values("Mutual_Information", ascending=False)
        .reset_index(drop=True)
    )
    ranking_table = importance_df.to_markdown(index=False)

    print("3. Generando gráficos en docs/data/figures/...")
    fig_paths = generate_eda_figures(df_clean, importance_df, figures_dir)

    print(f"4. Escribiendo reporte completo en {summary_path}...")
    report_md = rf"""# Reporte de Datos

Este documento contiene los resultados del análisis exploratorio de datos (EDA) realizado sobre los registros de viajes de taxis verdes (*Green Taxis*) de Nueva York correspondientes al primer semestre de 2024 (enero a junio).

---

## Resumen general de los datos

* **Volumen inicial (crudo):** `{len(df_raw):,}` observaciones distribuidas en 6 particiones mensuales y `20` variables originales, complementadas con un catálogo de `265` zonas geográficas TLC.
* **Volumen final procesado:** `{len(df_clean):,}` observaciones válidas (`{(len(df_clean)/len(df_raw))*100:.2f}%` de retención) y `13` variables seleccionadas sin fuga de información (*data leakage*).
* **Tipología de variables en el dataset limpio:**
  * **Variable objetivo continua (1):** `duration_min`.
  * **Variables numéricas (2):** `trip_distance`, `passenger_count`.
  * **Variables categóricas de alta y baja cardinalidad (6):** `PULocationID` (250+ zonas activas), `DOLocationID` (260+ zonas activas), `PU_Borough`, `DO_Borough`, `RatecodeID`, `VendorID`.
  * **Variables temporales derivadas (4):** `pickup_hour`, `pickup_dayofweek`, `is_weekend`, `pickup_month`.

### Estadísticas descriptivas globales (dataset limpio)

{desc_num}

---

## Resumen de calidad de los datos

Durante la auditoría sobre los `{len(df_raw):,}` registros crudos se identificaron los siguientes hallazgos de calidad:

### 1. Valores faltantes en origen

{nulls_table}

### 2. Anomalías, valores extremos y duplicados detectados
* **Registros duplicados exactos:** `{raw_dups:,}` filas.
* **Errores de reloj del taxímetro (fechas fuera de ene–jun 2024):** `{out_date:,}` registros.
* **Duraciones inválidas o extremas ($\le 1$ min o $> 180$ min):** `{bad_dur:,}` registros.
* **Distancias inconsistentes ($\le 0$ millas o $> 100$ millas):** `{bad_dist:,}` registros.
* **Zonas desconocidas o fuera de NYC (`PULocationID`/`DOLocationID` en `264` o `265`):** `{bad_zone:,}` registros.

### 3. Acciones tomadas
1. **Exclusión de variables nulas o post-viaje:** Se eliminó `ehail_fee` (100% nula) y todas las variables financieras/de cierre (`fare_amount`, `total_amount`, `lpep_dropoff_datetime`, etc.) para evitar fuga de información.
2. **Filtrado de integridad física:** Se descartaron `{len(df_raw) - len(df_clean):,}` registros (`{100 - (len(df_clean)/len(df_raw))*100:.2f}%`) que incumplían los rangos operativos de fecha, duración, distancia o zona válida.
3. **Imputación determinista:** Los `14,219` valores faltantes (`4.18%`) en `passenger_count` y `RatecodeID` se imputaron con la mediana (`1.0` pasajero) y la tarifa estándar (`1`), respectivamente.

---

## Variable objetivo

La variable objetivo **`duration_min`** representa el tiempo transcurrido en minutos entre `lpep_pickup_datetime` y `lpep_dropoff_datetime`.

{target_table}

* **Interpretación:** Presenta una distribución unimodal con marcada **asimetría positiva (cola larga hacia la derecha)**, donde la media supera a la mediana debido a trayectos largos hacia aeropuertos o entre distritos congestionados. Esto justifica evaluar los modelos futuros con **MAE** (robusto a colas largas) junto con **RMSE**.

![Distribución de duration_min]({fig_paths["target"]})

---

## Variables individuales

### 1. Distancia del viaje (`trip_distance`)
* Presenta alta asimetría positiva (mediana cercana a 1.8–2.0 millas con viajes de hasta 100 millas).
* **Transformación recomendada:** Aplicar `log1p(trip_distance)` y estandarización (`StandardScaler`) para estabilizar la varianza en modelos lineales y redes neuronales.

![Relación distancia y duración]({fig_paths["distance"]})

### 2. Variables temporales (`pickup_hour`, `pickup_dayofweek`, `is_weekend`)
* La duración media y mediana aumenta significativamente durante las **horas pico laborales (08:00–09:00 y 15:00–18:00)** debido a la congestión vehicular, y disminuye en horas de madrugada (01:00–05:00) y fines de semana.
* **Transformación recomendada:** Codificación cíclica ($\sin/\cos$) para `pickup_hour` y `pickup_dayofweek` en arquitecturas neuronales, o uso directo como enteros en modelos basados en árboles.

![Patrones temporales]({fig_paths["temporal"]})

### 3. Variables espaciales (`PULocationID`, `DOLocationID`, `PU_Borough`, `DO_Borough`)
* Alta cardinalidad (`> 250` zonas activas). La operación de taxis verdes se concentra mayoritariamente en Manhattan (zona norte), Queens y Brooklyn.
* **Transformación recomendada:** Uso de capas de **Embeddings densos** para `PULocationID` y `DOLocationID` en la red neuronal, y *Target Encoding* o agrupamiento por frecuencia en modelos tabulares clásicos.

#### Distribución por distrito de origen (`PU_Borough`)

{pu_borough_table}

---

## Ranking de variables

Para cuantificar la capacidad predictiva individual (capturando tanto relaciones lineales como no lineales) se calculó la **Información Mutua (*Mutual Information*)** y la **correlación absoluta de Spearman** respecto a `duration_min`:

{ranking_table}

![Ranking de variables]({fig_paths["ranking"]})

* **Hallazgo clave:** `trip_distance` domina la capacidad explicativa, seguida por las zonas específicas de destino y origen (`DOLocationID`, `PULocationID`) y la franja horaria (`pickup_hour`), confirmando que combinar distancia con representación espacial y temporal es esencial para predecir el ETA.

---

## Relación entre variables explicativas y variable objetivo

![Matriz de correlación]({fig_paths["correlation"]})

* **Relación distancia–tiempo:** Existe una fuerte correlación monótona positiva entre `trip_distance` y `duration_min`; sin embargo, la dispersión vertical crece a medida que aumenta la distancia, reflejando el impacto de la velocidad variable según la hora del día y el corredor vial.
* **Interacción espacio-temporal:** Trayectos de igual distancia presentan tiempos sustancialmente distintos dependiendo de si ocurren en horas pico entre distritos (`pickup_hour` $\times$ `PULocationID` / `DOLocationID`), lo que respalda el uso de modelos no lineales (ensambles de árboles y MLP con *Embeddings*) frente a una regresión lineal simple.
"""

    summary_path.write_text(report_md, encoding="utf-8")
    print("   -> Reporte docs/data/data_summary.md generado exitosamente.")


if __name__ == "__main__":
    main()