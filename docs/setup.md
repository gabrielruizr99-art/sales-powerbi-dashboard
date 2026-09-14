# Configuración local

Esta guía explica cómo preparar el entorno, limpiar el dataset, configurar PostgreSQL, cargar el modelo dimensional y abrir el proyecto PBIP. No almacenes contraseñas en el repositorio.

## 1. Requisitos

- Windows 10 u 11.
- Python 3.10 o superior.
- PostgreSQL instalado y en ejecución.
- Power BI Desktop con soporte para PBIP.
- Git, opcional para trabajar con control de versiones.

Comprueba las herramientas disponibles:

```powershell
py --version
psql --version
git --version
```

Si `psql` no está en `PATH`, utiliza su ruta de instalación, normalmente ubicada bajo `C:\Program Files\PostgreSQL\<versión>\bin\psql.exe`.

## 2. Preparar Python

Desde la raíz de `sales-powerbi-dashboard`, crea un entorno virtual:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Las dependencias funcionales son:

- `pandas`, para limpieza, transformación y control de calidad.
- `psycopg[binary]`, para conectar y cargar PostgreSQL.

Si PowerShell impide activar el entorno, puedes ejecutar los programas directamente:

```powershell
.venv\Scripts\python.exe python\clean_data.py
```

## 3. Limpiar y validar el dataset

Ejecuta:

```powershell
python python\clean_data.py
```

El script toma como entrada `data\raw\sales_data_ferreteria_10000.csv` y genera localmente:

```text
data\processed\sales_data_clean.csv
reports\data_quality_report.json
```

La validación revisa columnas obligatorias, identificadores duplicados, nulos, cantidades, precios, descuentos, márgenes y consistencia de importes, costos y utilidad. El proceso debe finalizar con estado `PASS`.

## 4. Instalar y comprobar PostgreSQL

Instala PostgreSQL mediante su instalador oficial o el gestor de paquetes disponible en Windows. Durante la instalación define una contraseña propia para el usuario administrador; PostgreSQL no proporciona una contraseña universal predeterminada.

Comprueba el servicio:

```powershell
Get-Service -Name "postgresql*"
```

Si está detenido, inicia el servicio correspondiente desde Servicios de Windows o con `Start-Service`, utilizando su nombre exacto.

Comprueba la conexión interactiva:

```powershell
psql -h localhost -p 5432 -U postgres -d postgres
```

`psql` solicitará la contraseña sin mostrarla en pantalla. Para salir, escribe `\q`.

## 5. Crear la base de datos

Ejecuta una sola vez:

```powershell
psql -h localhost -p 5432 -U postgres -d postgres -c "CREATE DATABASE sales_powerbi;"
```

Si la base ya existe, no es necesario volver a crearla. Puedes comprobarla con:

```powershell
psql -h localhost -p 5432 -U postgres -d postgres -c "SELECT datname FROM pg_database WHERE datname = 'sales_powerbi';"
```

## 6. Configurar credenciales en la sesión

Define los parámetros no sensibles:

```powershell
$env:PGHOST = "localhost"
$env:PGPORT = "5432"
$env:PGDATABASE = "sales_powerbi"
$env:PGUSER = "postgres"
```

Solicita la contraseña de forma interactiva y mantenla solo en la sesión actual:

```powershell
$pgSecure = Read-Host "Contraseña de PostgreSQL" -AsSecureString
$env:PGPASSWORD = [System.Net.NetworkCredential]::new("", $pgSecure).Password
```

No escribas la contraseña en README, scripts, capturas, commits ni archivos rastreados. `.env.example` contiene únicamente nombres y valores de ejemplo; el cargador utiliza las variables del proceso actual.

## 7. Ejecutar la carga

Con el CSV limpio disponible, ejecuta:

```powershell
python python\load_postgres.py
```

También puedes indicar otro CSV compatible:

```powershell
python python\load_postgres.py --csv "ruta\al\archivo.csv"
```

La carga:

1. Crea el esquema `bi_ferreteria` y sus tablas si no existen.
2. Crea una tabla temporal `stg_ventas`.
3. Copia el CSV mediante `COPY FROM STDIN`.
4. Inserta o actualiza las dimensiones.
5. Inserta o actualiza `fact_ventas` mediante `venta_id`.
6. Crea la vista `bi_ferreteria.vw_ventas_powerbi`.
7. Muestra el conteo final de cada tabla.

La operación puede repetirse sin duplicar ventas porque utiliza actualizaciones por conflicto de clave.

Al terminar, elimina la contraseña de la sesión:

```powershell
Remove-Item Env:PGPASSWORD
Remove-Variable pgSecure -ErrorAction SilentlyContinue
```

## 8. Verificar la base

Abre `psql` sobre la base cargada:

```powershell
psql -h localhost -p 5432 -U postgres -d sales_powerbi
```

Ejecuta consultas de comprobación:

```sql
SELECT COUNT(*) FROM bi_ferreteria.fact_ventas;
SELECT COUNT(*) FROM bi_ferreteria.dim_producto;
SELECT MIN(fecha_key), MAX(fecha_key) FROM bi_ferreteria.dim_fecha;
SELECT * FROM bi_ferreteria.vw_ventas_powerbi LIMIT 5;
```

## 9. Abrir el proyecto PBIP

Con PostgreSQL disponible, abre en Power BI Desktop:

```text
powerbi\sales-powerbi.pbip
```

El proyecto contiene una carpeta `.Report` en PBIR y una carpeta `.SemanticModel` en TMDL. Si Power BI solicita credenciales, configúralas únicamente mediante el cuadro de origen de datos de tu instalación local.

No publiques el informe ni confirmes archivos locales de caché. Antes de trabajar con Git, cierra Power BI Desktop o comprueba que no existan cambios sin guardar.

## Solución de problemas

### `psql` no se reconoce

Agrega temporalmente la carpeta `bin` de PostgreSQL al `PATH` de la sesión o invoca `psql.exe` mediante su ruta completa.

### Falló la autenticación del usuario `postgres`

Comprueba el usuario, el puerto y la contraseña definida durante la instalación. No existe una contraseña predeterminada que funcione en todas las instalaciones.

### Falta `PGPASSWORD`

Vuelve a ejecutar el bloque de lectura segura en la misma terminal donde ejecutarás `load_postgres.py`.

### No existe el CSV limpio

Ejecuta primero:

```powershell
python python\clean_data.py
```

### Power BI no puede actualizar

Comprueba que PostgreSQL esté activo, que la base `sales_powerbi` exista y que las credenciales del origen estén configuradas en Power BI Desktop.
