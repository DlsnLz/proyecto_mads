from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from nombre_paquete.database.loader import load_raw_trips, load_zone_lookup
from nombre_paquete.preprocessing.cleaning import clean_and_enrich_trips


def main() -> None:
    raw_dir = PROJECT_ROOT / "data" / "raw"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = processed_dir / "green_trips_2024_h1_clean.parquet"

    print("=== EJECUTANDO PREPROCESAMIENTO BASE ===")
    df_raw = load_raw_trips(raw_dir)
    df_zones = load_zone_lookup(raw_dir)

    df_clean = clean_and_enrich_trips(df_raw, df_zones)
    retention = (len(df_clean) / len(df_raw)) * 100
    print(f"Registros crudos:  {len(df_raw):,}")
    print(f"Registros limpios: {len(df_clean):,} ({retention:.2f}% retenidos)")

    df_clean.to_parquet(output_path, index=False, compression="snappy")
    print(f"Dataset limpio guardado en: {output_path}")


if __name__ == "__main__":
    main()