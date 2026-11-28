# Diccionario de Datos - Registros de Viajes LPEP

**Fecha:** 18 de marzo de 2025

Este diccionario de datos describe los datos de viajes SHL (Street Hail Livery / taxis verdes).

| Nombre del Campo (Field Name) | Descripción |
| :--- | :--- |
| **VendorID** | Código que indica el proveedor de LPEP que proporcionó el registro.<br>• `1` = Creative Mobile Technologies, LLC<br>• `2` = Curb Mobility, LLC<br>• `6` = Myle Technologies Inc |
| **lpep_pickup_datetime** | La fecha y hora en que se activó el taxímetro. |
| **lpep_dropoff_datetime** | La fecha y hora en que se desactivó el taxímetro. |
| **store_and_fwd_flag** | Este indicador señala si el registro del viaje se almacenó en la memoria del vehículo antes de enviarse al proveedor (conocido como *«store and forward»* o almacenar y reenviar), debido a que el vehículo no tenía conexión con el servidor. |
| **RatecodeID** | El código de tarifa final vigente al término del viaje.<br>• `1` = Tarifa estándar (*Standard rate*)<br>• `2` = JFK<br>• `3` = Newark<br>• `4` = Nassau o Westchester<br>• `5` = Tarifa negociada (*Negotiated fare*)<br>• `6` = Viaje compartido (*Group ride*)<br>• `99` = Nulo / desconocido (*Null/unknown*) |
| **PULocationID** | Zona de Taxi de la TLC en la que se activó el taxímetro. |
| **DOLocationID** | Zona de Taxi de la TLC en la que se desactivó el taxímetro. |
| **passenger_count** | El número de pasajeros en el vehículo. |
| **trip_distance** | La distancia transcurrida del viaje en millas, reportada por el taxímetro. |
| **fare_amount** | La tarifa por tiempo y distancia calculada por el taxímetro. Para obtener información adicional sobre las siguientes columnas, consulte: [https://www.nyc.gov/site/tlc/passengers/taxi-fare.page](https://www.nyc.gov/site/tlc/passengers/taxi-fare.page) |
| **extra** | Cargos adicionales y recargos misceláneos. |
| **mta_tax** | Impuesto que se aplica automáticamente según la tarifa medida en uso. |
| **tip_amount** | Monto de la propina: este campo se completa automáticamente para las propinas pagadas con tarjeta de crédito. No se incluyen las propinas en efectivo. |
| **tolls_amount** | Monto total de todos los peajes pagados durante el viaje. |
| **improvement_surcharge** | Recargo por mejoras (*improvement surcharge*) aplicado a los viajes al bajar la bandera (iniciar el taxímetro). Este recargo comenzó a cobrarse en 2015. |
| **total_amount** | El monto total cobrado a los pasajeros. No incluye propinas en efectivo. |
| **payment_type** | Código numérico que indica cómo pagó el pasajero el viaje.<br>• `0` = Viaje con tarifa flexible (*Flex Fare trip*)<br>• `1` = Tarjeta de crédito (*Credit card*)<br>• `2` = Efectivo (*Cash*)<br>• `3` = Sin cargo (*No charge*)<br>• `4` = En disputa (*Dispute*)<br>• `5` = Desconocido (*Unknown*)<br>• `6` = Viaje anulado (*Voided trip*) |
| **trip_type** | Código que indica si el viaje fue tomado en la calle (*street-hail*) o por despacho (*dispatch*), el cual se asigna automáticamente según la tarifa medida en uso, pero puede ser modificado por el conductor.<br>• `1` = En la calle (*Street-hail*)<br>• `2` = Por despacho (*Dispatch*) |
| **congestion_surcharge** | Monto total recaudado en el viaje correspondiente al recargo por congestión del estado de Nueva York (NYS). |
| **cbd_congestion_fee** | Cargo por viaje correspondiente a la Zona de Alivio de Congestión de la MTA (*MTA's Congestion Relief Zone*), vigente a partir del 5 de enero de 2025. |

# Recuperado

- New York City Taxi and Limousine Commission. (2025, 18 de marzo). Data dictionary – LPEP trip records. [Diccionario oficial de taxis verdes.](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_green.pdf)