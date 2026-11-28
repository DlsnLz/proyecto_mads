from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

from nombre_paquete.database.loader import (
    extract_schema_summary,
    load_raw_trips,
    load_zone_lookup,
)


def main() -> None:
    raw_dir = PROJECT_ROOT / "data" / "raw"
    print("=== AUDITORÍA DE ADQUISICIÓN DE DATOS ===")
    df_raw = load_raw_trips(raw_dir)
    df_zones = load_zone_lookup(raw_dir)

    print(f"Total registros crudos (ene-jun 2024): {len(df_raw):,}")
    print(f"Total zonas en catálogo TLC: {len(df_zones):,}\n")
    print(extract_schema_summary(df_raw).to_string(index=False))


if __name__ == "__main__":
    main()