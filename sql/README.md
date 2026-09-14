# PostgreSQL

Los scripts se ejecutan automáticamente mediante `python/load_postgres.py` en este orden:

1. `01_schema.sql`: crea el esquema dimensional y sus índices.
2. `02_transform.sql`: transforma la tabla temporal y carga dimensiones y hechos.
3. `03_views.sql`: crea una vista plana para validación y exploración inicial.

La carga es idempotente. Si un `venta_id` ya existe, sus datos se actualizan en lugar de duplicarse.

