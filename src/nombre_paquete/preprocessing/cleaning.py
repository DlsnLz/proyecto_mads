import pandas as pd

INVALID_ZONES = {264, 265}


def clean_and_enrich_trips(
    df_trips: pd.DataFrame, df_zones: pd.DataFrame
) -> pd.DataFrame:
    """Calcula duration_min, filtra anomalías, enriquece zonas y previene leakage."""
    df = df_trips.copy()

    df["lpep_pickup_datetime"] = pd.to_datetime(df["lpep_pickup_datetime"])
    df["lpep_dropoff_datetime"] = pd.to_datetime(df["lpep_dropoff_datetime"])

    # Filtrar estrictamente ene-jun 2024
    df = df[
        (df["lpep_pickup_datetime"] >= pd.Timestamp("2024-01-01"))
        & (df["lpep_pickup_datetime"] < pd.Timestamp("2024-07-01"))
    ]

    # Target: duración en minutos
    df["duration_min"] = (
        df["lpep_dropoff_datetime"] - df["lpep_pickup_datetime"]
    ).dt.total_seconds() / 60.0

    # Filtrado de calidad
    df = df[
        (df["duration_min"] > 1.0)
        & (df["duration_min"] <= 180.0)
        & (df["trip_distance"] > 0.0)
        & (df["trip_distance"] <= 100.0)
    ]

    df = df.dropna(subset=["PULocationID", "DOLocationID"])
    df["PULocationID"] = df["PULocationID"].astype("int32")
    df["DOLocationID"] = df["DOLocationID"].astype("int32")
    df = df[
        (~df["PULocationID"].isin(INVALID_ZONES))
        & (~df["DOLocationID"].isin(INVALID_ZONES))
    ]

    # Cruce con catálogo de zonas
    zone_map = df_zones[["LocationID", "Borough"]].drop_duplicates("LocationID")
    df = df.merge(
        zone_map.rename(columns={"LocationID": "PULocationID", "Borough": "PU_Borough"}),
        on="PULocationID",
        how="left",
    ).merge(
        zone_map.rename(columns={"LocationID": "DOLocationID", "Borough": "DO_Borough"}),
        on="DOLocationID",
        how="left",
    )
    df["PU_Borough"] = df["PU_Borough"].fillna("Unknown").astype("string")
    df["DO_Borough"] = df["DO_Borough"].fillna("Unknown").astype("string")

    # Variables temporales
    df["pickup_hour"] = df["lpep_pickup_datetime"].dt.hour.astype("int8")
    df["pickup_dayofweek"] = df["lpep_pickup_datetime"].dt.dayofweek.astype("int8")
    df["is_weekend"] = (df["pickup_dayofweek"] >= 5).astype("int8")
    df["pickup_month"] = df["lpep_pickup_datetime"].dt.month.astype("int8")

    # Imputación controlada
    df["passenger_count"] = (
        df["passenger_count"].fillna(df["passenger_count"].median()).astype("float32")
    )
    df["RatecodeID"] = df["RatecodeID"].fillna(1).astype("int8")
    df["VendorID"] = df["VendorID"].fillna(2).astype("int8")
    df["trip_distance"] = df["trip_distance"].astype("float64")
    df["duration_min"] = df["duration_min"].astype("float64")

    final_columns = [
        "duration_min",
        "PULocationID",
        "DOLocationID",
        "PU_Borough",
        "DO_Borough",
        "trip_distance",
        "pickup_hour",
        "pickup_dayofweek",
        "is_weekend",
        "pickup_month",
        "RatecodeID",
        "VendorID",
        "passenger_count",
    ]
    return df[final_columns].reset_index(drop=True)