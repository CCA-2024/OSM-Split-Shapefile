from shapely.geometry import Polygon, LinearRing
import geopandas as gpd
from glob import glob
import unicodedata
import zipfile
import os
import re

class UFGeo:
    
    def __init__(self):
        self.base_path = 'Modules'
        self.module_path = 'UFs'
        self.geojsons = os.path.join(self.base_path, self.module_path, 'GeoJsons', '*.geojson')
        for path in glob(self.geojsons):
            os.system(f"rm -f {path}")
        
    def fechar_geometria(self, geometry):
        """
        Verifica se a geometria é fechada. Se não for, fecha-a.

        Args:
            geometry: Objeto Shapely (Polygon ou LinearRing).

        Returns:
            geometry: Geometria fechada.
        """
        if isinstance(geometry, Polygon):
            if geometry.exterior.coords[0] != geometry.exterior.coords[-1]:
                closed_exterior = list(geometry.exterior.coords) + [geometry.exterior.coords[0]]
                return Polygon(closed_exterior)
            else:
                return geometry
        elif isinstance(geometry, LinearRing):
            if not geometry.is_ring:
                coords = list(geometry.coords) + [geometry.coords[0]]
                return LinearRing(coords)
            else:
                return geometry
        else:
            raise TypeError("A geometria deve ser Polygon ou LinearRing.")

    def __unicode(self, texto: str) -> str:
        # Normaliza o texto, removendo os acentos
        texto_normalizado = unicodedata.normalize('NFD', texto)
        texto_sem_acento = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
        
        # Filtra apenas as letras (removendo números e caracteres especiais)
        texto_limpo = ''.join(c for c in texto_sem_acento if c.isalpha() or c == '-')
        return texto_limpo

    def unzip_shapefile(self):
        """Descompacta arquivos ZIP contendo shapefiles."""
        zip_path = os.path.join(self.base_path, self.module_path, 'ZipFile', '*.zip')
        extract_path = os.path.join(self.base_path, self.module_path, 'Shapfile',)
        for path in [file for file in glob(self.geojsons) if '.metadata' not in file]:
            os.system(f"rm -f {path}")
            
        print(glob(zip_path))
        with zipfile.ZipFile(glob(zip_path)[0], "r") as zip_ref:
            zip_ref.extractall(extract_path)
        return extract_path

    def read_shapefile(self):
        """Lê um shapefile do diretório descompactado."""
        shapefile_path = os.path.join(self.base_path, self.module_path, 'Shapfile', '*.shp')
        return gpd.read_file(glob(shapefile_path)[0])

    def simplify_geometry(self, gdf, tolerance=0.01):
        """Simplifica as geometrias de um GeoDataFrame."""
        gdf.geometry = gdf.geometry.apply(lambda x: x.simplify(tolerance) if x.is_valid else x)
        return gdf

    def save_as_geojson(self, gdf):
        """Transforma um GeoDataFrame em GeoJSON e salva."""
        shapefile_path = os.path.join(self.base_path, self.module_path, 'Shapfile', '*.shp')
        filename = f"{os.path.splitext(os.path.basename(glob(shapefile_path)[0]))[0]}.geojson"
        geojson_path = os.path.join(self.base_path, self.module_path, 'GeoJsons', filename)
        gdf["FILENAME"] = gdf["NM_UF"] + '-' + gdf["SIGLA_UF"]
        for _, geojson in gdf.iterrows():
            path_to_save = os.path.splitext(os.path.basename(filename))[0] 
            gdf.query(f"FILENAME == '{geojson.FILENAME}'")\
               .to_file(geojson_path.replace(path_to_save, self.__unicode(geojson.FILENAME)), driver='GeoJSON')
        return os.path.join(self.base_path, self.module_path, 'GeoJsons', "*.geojson")

    def process_geojson(self, gdf):
        """Processa o GeoJSON, fechando geometrias e selecionando as maiores áreas."""
        gdf = gdf.explode(index_parts=False)
        gdf.geometry = gdf.geometry.apply(self.fechar_geometria)
        gdf["AREA_KM2"] = gdf.geometry.apply(lambda x: x.area)
        gdf["KEY"] = gdf["NM_UF"] + gdf["AREA_KM2"].apply(lambda x: str(x))

        grouped = gdf.groupby("NM_UF").max("AREA_KM2").reset_index(drop=False)
        grouped["KEY"] = grouped["NM_UF"] + grouped["AREA_KM2"].apply(lambda x: str(x))

        final_gdf = gdf[gdf.KEY.isin(grouped.KEY)].copy()
        final_gdf.drop(["KEY", "AREA_KM2"], axis=1, inplace=True)

        return final_gdf

    def execute(self):
        """Executa todo o pipeline de processamento."""
        # Descompactar shapefiles
        self.unzip_shapefile()

        # Ler shapefile
        shapefile = self.read_shapefile()

        # Simplificar geometria
        simplified = self.simplify_geometry(shapefile)

        # Processar GeoJSON para ajustar e selecionar maiores áreas
        processed_geojson_path = self.process_geojson(simplified)

        # Salvar como GeoJSON
        return self.save_as_geojson(processed_geojson_path)
