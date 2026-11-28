from pathlib import Path
import pandas as pd

EXPECTED_PARQUET_FILES = [
    f"green_tripdata_2024-{month:02d}.parquet" for month in range(1, 7)
]
ZONE_LOOKUP_FILE = "taxi_zone_lookup.csv"


def load_raw_trips(raw_dir: Path) -> pd.DataFrame:
    """Carga y concatena los archivos Parquet de enero a junio de 2024."""
    frames = []
    for filename in EXPECTED_PARQUET_FILES:
        file_path = raw_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(
                f"No se encontró {file_path}. Ejecuta 'dvc pull' primero."
            )
        frames.append(pd.read_parquet(file_path))
    return pd.concat(frames, ignore_index=True)


def load_zone_lookup(raw_dir: Path) -> pd.DataFrame:
    """Carga el catálogo oficial de zonas TLC."""
    lookup_path = raw_dir / ZONE_LOOKUP_FILE
    if not lookup_path.exists():
        raise FileNotFoundError(
            f"No se encontró {lookup_path}. Ejecuta 'dvc pull' primero."
        )
    return pd.read_csv(lookup_path)


def extract_schema_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve nombre de columna, tipo de dato, nulos y porcentaje de nulos."""
    return pd.DataFrame(
        {
            "Columna": df.columns,
            "Tipo": [str(dtype) for dtype in df.dtypes],
            "Nulos": df.isna().sum().values,
            "Porcentaje_Nulos": (df.isna().mean() * 100).round(2).values,
        }
    )