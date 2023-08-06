INEGIpy es una librería para interactuar fácilmente con los datos del Instituto Nacional de Geografía y Estadística (INEGI) desde Python. Su propósito es apoyar en la creación de consultas automatizadas y  en el acceso a la información para el análisis de datos. 

De la información que ofrece el INEGI actualmente se cuenta con una clase dedicada al Banco de Indicadores, otra dedicada al DENUE, otra a la información del Marco Geoestadístico y finalmente una dedicada al Sistema de Ruteo de México.

También se encuentra en constrcción un módulo de Series dedicado a consultas automatizadas de los principales indicadores económicos como el PIB, INPC, Ocupación, etc. 

*Principales características*

* Permite un acceso rápido a las bases de datos del INEGI sin necesidad de descargas.
* Regresa la información en DataFrames o GeoDataFrames listos para su uso en Python.
* Para el caso de los indicadores económicos, el DataFrame resultante cuenta con un DateTimeIndex y una columna para cada indicador.
* Para las bases con información georeferenciada (DENUE, Marco Geoestadístico y Ruteo) se regresa un GeoDataFrame listo para realizar operaciones espaciales. 

    * El DENUE obtiene tanto la ubicción de los establecimientos como información sobre la actividad económica y el número de trabajadores.
    * El Marco Geoestadístico permite obtener la información de la población según el Censo de Población y Vivienda del 2020 así como la información vectorial de las áreas que se especifiquen en cualquier nivel de agregación espacial. Evita descargar un montón de archivos Shape para realizar mapas y operaciones espaciales.
    * El Servicio de Ruteo además de calcular rutas entre puntos ofrece información georeferenciada sobre diferentes destinos los cuales pueden ser destinos turísticos o lugares de interés como aeropuertos, puertos, servicios médicos, o centros educativos de nivel superior. También ofrece detalles sobre el costo de las rutas y los precios promedio de los combustibles. 

*Requerimientos*

* pandas
* numpy
* requests
* shapely
* geopandas

La instalación de GeoPandas puede ser un poco complicada de manejar por lo que se recomieda instalarla previemente: https://geopandas.org/en/stable/getting_started/install.html

Más información en: https://github.com/andreslomeliv/DatosMex/tree/master/INEGIpy