# Project Charter – Entendimiento del negocio

## Nombre del proyecto

Predicción de la duración de viajes en taxis verdes de Nueva York mediante una red neuronal.

## Problema de negocio

Cuando un pasajero aborda un taxi verde e indica su destino, quiere saber cuánto tardará en llegar. El proyecto estimará la duración del trayecto en minutos a partir de las zonas de origen y destino, la hora de salida y el día de la semana. Al sumar la duración estimada a la hora de salida se obtiene la hora estimada de llegada (ETA).

## Objetivo general

Evaluar el desempeño de una red neuronal en la predicción de la duración de viajes en taxis verdes de Nueva York al inicio del servicio, mediante una comparación con regresión lineal sobre viajes de un mes posterior al entrenamiento.

## Alcance

### Entregables

- Un conjunto de datos reproducible a partir de los archivos Parquet de taxis verdes de enero a junio de 2024 (abril a junio se usarán para el monitoreo de drift), versionado con DVC, y del catálogo oficial de zonas `taxi_zone_lookup.csv`.
- Dos modelos de regresión con las mismas variables de entrada. La línea base será una regresión lineal con codificación *one-hot* de las zonas. El modelo de Deep Learning será un perceptrón multicapa (MLP) que aprenderá una representación vectorial (*embedding*) para las zonas de origen y destino.
- Un registro de experimentos en MLflow, el modelo ganador registrado en el Model Registry, una API con FastAPI (POST /predict) que reciba las dos zonas y la fecha y hora de salida y devuelva la duración estimada en minutos, y un informe de evaluación.

### Ampliaciones

XGBoost será la primera comparación adicional si el cronograma lo permite. También se podrá extender la evaluación hasta diciembre de 2024 e incorporar Optuna.

### Fuera de alcance

Se excluyen los taxis amarillos y otros servicios de transporte, la espera previa al abordaje, la integración de tráfico o clima en tiempo real, el cálculo de tarifas, la asignación de conductores y el desarrollo de una interfaz gráfica.

## Metodología

Se seguirá CRISP-DM con un registro reproducible de los experimentos.

1. **Comprensión y preparación de los datos.** Se calculará `duration_min` como la diferencia en minutos entre `lpep_dropoff_datetime` y `lpep_pickup_datetime`. Se documentarán los registros incompletos y las duraciones no positivas. Los viajes de más de 60 minutos se revisarán antes de fijar un límite. Las reglas de depuración se definirán con enero y se aplicarán por igual a los meses siguientes.
2. **Variables disponibles al abordar.** Se utilizarán la zona de origen (`PULocationID`), la zona de destino, la hora y el día de la semana. La TLC registra en `DOLocationID` la zona donde terminó el viaje. Para el experimento se asumirá que coincide con el destino indicado por el pasajero al abordar. Se excluirá de las entradas `trip_distance` porque el taxímetro registra la distancia efectivamente recorrida.
3. **Entrenamiento y validación temporal.** Se entrenarán ambos modelos con enero de 2024 y se usará febrero para elegir sus configuraciones. Una vez fijadas, se reentrenarán ambos modelos con enero y febrero y se evaluarán sobre los mismos viajes de marzo. MLflow registrará los parámetros, las métricas y los modelos obtenidos.

## Criterios de evaluación

- **RMSE en minutos.** Será la métrica principal. Se calculará la reducción porcentual del RMSE de la red frente a la regresión lineal. Un valor negativo indicará que la línea base obtuvo menor error.
- **MAE en minutos.** Mostrará cuántos minutos se desvía, en promedio, una predicción de la duración real, tomando el valor absoluto de cada error.
- **Porcentaje de viajes con error absoluto de hasta cinco minutos.** Indicará con qué frecuencia la estimación queda dentro de ese margen para el pasajero.

El informe comparará ambos modelos en marzo e identificará en qué rutas se concentran los errores, indicando cuántos viajes respaldan cada comparación. La conclusión se basará en los resultados observados, incluso si la regresión lineal obtiene el menor RMSE.

## Cronograma

| Fechas de 2026 | Actividad y resultado esperado |
|---|---|
| 23–29 de noviembre | Preparar los datos, documentar los filtros y obtener las primeras métricas de la regresión lineal en febrero. |
| 30 de noviembre–6 de diciembre | Entrenar la red con *embeddings* y comparar ambos modelos en febrero. |
| 7–13 de diciembre | Cerrar las configuraciones, reentrenar con enero y febrero, evaluar en marzo y analizar los errores. |
| 14–19 de diciembre | Completar la demostración, el informe reproducible y la sustentación. |

## Equipo del proyecto

| Integrante | Formación |
|---|---|
| Dilson Lazaro Ospino | Estadístico e ingeniero de sistemas |
| Daniel Esteban Molina Sánchez | Ingeniero de ciencias computacionales |
| Sebastian Paez Rojas | Ingeniero químico |

## Presupuesto estimado

| Concepto | Costo estimado (USD) |
|---|---:|
| Dedicación a ciencia de datos y modelamiento | 2.500 |
| Dedicación a ingeniería de datos y MLOps | 2.500 |
| Cómputo, almacenamiento y licencias con los recursos disponibles | 0 |
| Contingencia del 10 % sobre el valor del trabajo | 500 |
| **Total estimado** | **5.500** |

Los USD 5.000 de personal representan el valor estimado del trabajo académico del equipo. Los USD 500 restantes corresponden a una reserva para imprevistos.

## Partes interesadas

- **Pasajeros de taxis verdes.** Son los usuarios de referencia para la estimación de la duración al abordar.
- **Operadores de flotas.** Son usuarios potenciales de la estimación para informar a sus pasajeros.
- **Equipo del proyecto y docente de la asignatura.** Desarrollan y evalúan, respectivamente, la metodología, la reproducibilidad y los resultados.

## Aprobaciones

 - Dilson Lazaro Ospino (DlsnLz)

## Bibliografía

- New York City Taxi and Limousine Commission. (s. f.). *TLC trip record data* [Conjunto de datos]. City of New York. [Portal oficial de datos y catálogo de zonas](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page).
- New York City Taxi and Limousine Commission. (2025, 18 de marzo). *Data dictionary – LPEP trip records*. [Diccionario oficial de taxis verdes](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_green.pdf).
- Gorishniy, Y., Rubachev, I., Khrulkov, V., & Babenko, A. (2021). Revisiting deep learning models for tabular data. *Advances in Neural Information Processing Systems, 34*. [Artículo en NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2021/hash/9d86d83f925f2149e9edb0ac3b49229c-Abstract.html).
