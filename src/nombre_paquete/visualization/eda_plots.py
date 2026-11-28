from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")


def generate_eda_figures(
    df_clean: pd.DataFrame, importance_df: pd.DataFrame, figures_dir: Path
) -> dict[str, str]:
    """Genera y guarda los gráficos del EDA en docs/data/figures/."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    paths = {}

    # 1. Distribución de la variable objetivo (duration_min)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    sns.histplot(
        df_clean["duration_min"], bins=60, kde=True, color="#1f77b4", ax=axes[0]
    )
    axes[0].axvline(
        df_clean["duration_min"].median(),
        color="red",
        linestyle="--",
        label=f"Mediana: {df_clean['duration_min'].median():.2f} min",
    )
    axes[0].set_title("Distribución de duration_min (0 a 180 min)")
    axes[0].set_xlabel("Duración (minutos)")
    axes[0].set_ylabel("Frecuencia")
    axes[0].legend()

    sns.boxplot(x=df_clean["duration_min"], color="#4c9be8", ax=axes[1])
    axes[1].set_title("Diagrama de caja de duration_min")
    axes[1].set_xlabel("Duración (minutos)")
    plt.tight_layout()
    p1 = figures_dir / "01_target_distribution.png"
    plt.savefig(p1, dpi=150)
    plt.close()
    paths["target"] = "figures/01_target_distribution.png"

    # 2. Relación trip_distance vs duration_min (muestra aleatoria de 15,000 viajes)
    sample = df_clean.sample(n=min(15000, len(df_clean)), random_state=42)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    sns.scatterplot(
        data=sample,
        x="trip_distance",
        y="duration_min",
        alpha=0.25,
        s=12,
        color="#2ca02c",
        ax=axes[0],
    )
    axes[0].set_xlim(0, 35)
    axes[0].set_ylim(0, 120)
    axes[0].set_title("Dispersión: Distancia vs. Duración")
    axes[0].set_xlabel("Distancia del viaje (millas)")
    axes[0].set_ylabel("Duración (minutos)")

    sns.histplot(np.log1p(df_clean["trip_distance"]), bins=50, color="#2ca02c", ax=axes[1])
    axes[1].set_title("Distribución transformada log1p(trip_distance)")
    axes[1].set_xlabel("log1p(trip_distance)")
    axes[1].set_ylabel("Frecuencia")
    plt.tight_layout()
    p2 = figures_dir / "02_distance_vs_duration.png"
    plt.savefig(p2, dpi=150)
    plt.close()
    paths["distance"] = "figures/02_distance_vs_duration.png"

    # 3. Patrones temporales: Hora del día y Día de la semana
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    hourly = (
        df_clean.groupby("pickup_hour")["duration_min"]
        .agg(["mean", "median"])
        .reset_index()
    )
    axes[0].plot(hourly["pickup_hour"], hourly["mean"], marker="o", label="Media")
    axes[0].plot(hourly["pickup_hour"], hourly["median"], marker="s", label="Mediana")
    axes[0].set_title("Duración de viaje por hora de recogida")
    axes[0].set_xlabel("Hora del día (0-23)")
    axes[0].set_ylabel("Duración (minutos)")
    axes[0].set_xticks(range(0, 24, 2))
    axes[0].legend()

    days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    daily = df_clean.groupby("pickup_dayofweek")["duration_min"].median().reset_index()
    sns.barplot(
        x=[days[d] for d in daily["pickup_dayofweek"]],
        y=daily["duration_min"],
        palette="viridis",
        hue=[days[d] for d in daily["pickup_dayofweek"]],
        legend=False,
        ax=axes[1],
    )
    axes[1].set_title("Mediana de duración por día de la semana")
    axes[1].set_xlabel("Día de la semana")
    axes[1].set_ylabel("Mediana de duración (min)")
    plt.tight_layout()
    p3 = figures_dir / "03_temporal_patterns.png"
    plt.savefig(p3, dpi=150)
    plt.close()
    paths["temporal"] = "figures/03_temporal_patterns.png"

    # 4. Ranking de variables (Mutual Information)
    plt.figure(figsize=(9, 4.5))
    sns.barplot(
        data=importance_df,
        x="Mutual_Information",
        y="Variable",
        palette="mako",
        hue="Variable",
        legend=False,
    )
    plt.title("Ranking de importancia predictiva (Información Mutua vs. duration_min)")
    plt.xlabel("Información Mutua (nats)")
    plt.ylabel("Variable explicativa")
    plt.tight_layout()
    p4 = figures_dir / "04_feature_ranking.png"
    plt.savefig(p4, dpi=150)
    plt.close()
    paths["ranking"] = "figures/04_feature_ranking.png"

    # 5. Matriz de correlación (Spearman)
    num_cols = [
        "duration_min",
        "trip_distance",
        "PULocationID",
        "DOLocationID",
        "pickup_hour",
        "pickup_dayofweek",
        "is_weekend",
        "RatecodeID",
        "passenger_count",
    ]
    corr = df_clean[num_cols].corr(method="spearman")
    plt.figure(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, square=True)
    plt.title("Matriz de correlación de Spearman")
    plt.tight_layout()
    p5 = figures_dir / "05_correlation_matrix.png"
    plt.savefig(p5, dpi=150)
    plt.close()
    paths["correlation"] = "figures/05_correlation_matrix.png"

    return paths