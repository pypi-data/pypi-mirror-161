Conversor GNSS a GeoJSONData
==================================

Este módulo permite convertir los datos generados por una estación GNSS Trimble y
emitido por GSOF a una estructura de *Geojson*.

Se inicializa:

```python
from data_geo import GeoJSONData
kwargs=dict(
    station="CODE"
    position=<<diccionario ECEF* y lat-lon-z>>)
process=GeoJSONData(**kwargs**)
```
Debe contener las tablas ECEF y VCV al menos para poder realizar la conversión.


Se transforma set de datos.

```python
for data in lista:
    print(process.manage_data(data))

```

## Registro logs


Si ocurre algún error estos se registran en el log asignado a *log_path*
