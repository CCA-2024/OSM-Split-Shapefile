# OSM Split Shapefile

<div align="center">
    <img src="./ico/logo-fmr.png"       alt="FMR"       style="margin: 0 10px; height: 70px;    width: 200px" />
    <img src="./ico/logo-disbral.png"   alt="Disbral"   style="margin: 0 10px; height: 100px;   width: 300px" />
    <img src="./ico/logo-enapa.png"     alt="ENAPA"     style="margin: 0 10px; height: 70px;    width: 200px" />
</div>
<hr/>
<br>

**Note:** This project was developed by Distribuidora Brasileira de Asfalto (Disbral) and is free to use, through the Automation Control Center (CCA) department, to address memory overflow issues in Docker containers when deploying PGRouter with OSM data for the entire country. The adopted approach enables incremental and partitioned loading by federative unit (UF), ensuring lower memory consumption and making it feasible to obtain a router with the complete road network of the country. [Disbral WebSite](https://www.grupodisbral.com.br/).
<br>

## 0° Step - ( Optional )
- If you want to save the `*.osm` files in a different folder than the current project, update the `PATHSAVE` environment variable in the .env file.

## 1° Step
 - Download your country osm grahp in [Geofabrik](https://download.geofabrik.de/)
 - Save Your file downloaded *.pbf in `PROTOBUF\PROTOBUF\<Your File>.pbf`

## 2° Step
 - Download your shapefile with state boundaries from your country's organization website in zip format, for the Brasil [here](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html).
 - Check if your zip file contains files with the following extensions: `*.cpg, *.dbf, *.prj, *.shp, *.shx`
 - Save Your zip file in `Modules\UFs\ZipFile\<Your File>.zip`

 ## 3° Step
 - Open cmd and acess `src\`
 - Run `Docker compose up --build -d`
 - Finish Your have `*.pbf` files by UF's !!

<br>

**Obs:** Note that the project includes a .env file with the `SIZELIMIT` variable, which sets the maximum size allowed for processed files. The default value is set to avoid memory issues, but can be adjusted as needed. Keep in mind that a `130 MB *.pbf` file generates approximately `1.3 GB` in `*.osm` format, consuming about `8 GB of RAM` when processed in the container.

* Cropping files based on the value set in `SIZELIMIT` is not exact, but the final sizes will be close to the specified limit and will be significantly reduced.

* The system may generate cropped files with inaccurate final sizes because it assumes that the road network is homogeneous, making equal divisions. Although this does not reflect reality, the method remains functional.
