# OSM Split UF's

![Disbral](https://www.grupodisbral.com.br/assets/img/footer-logo.png) -
![FMR](https://www.grupodisbral.com.br/assets/img/2.png) -
![ENAPA](https://www.grupodisbral.com.br/assets/img/3.png)

**Note** This project was developed by Disbral, through the Automation Control Center (CCA) department, to address memory overflow issues in Docker containers when deploying PGRouter with OSM data for the entire country. The adopted approach enables incremental and partitioned loading by federative unit (UF), ensuring lower memory consumption and making it feasible to obtain a router with the complete road network of the country.

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