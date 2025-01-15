from Modules.Config.env import configRun
from shapely.geometry import Polygon
from Modules.UFs.Engine import UFGeo
from bs4 import BeautifulSoup
import geopandas as gpd
from glob import glob
import math
import time
import os
import subprocess

class OSMSplit:
    """
    Objeto responsavel por recortar o protobuf do pais em estados
    isso diminui a sobrecarga de ram na hora de carregar a malha 
    viaria
    """
    
    def __init__(self):
        self.path_protobuf = os.path.join('PROTOBUF','PROTOBUF')
        self.path_protobufs = os.path.join('PROTOBUF','PROTOBUFs')
        if not os.path.exists(self.path_protobuf):
            os.makedirs(self.path_protobuf)
        if not os.path.exists(self.path_protobufs):
            os.makedirs(self.path_protobuf)
            
        self.keys_reprocess = {}
        self.UFProcessor = UFGeo()
        self.PathGeoJsons = self.UFProcessor.execute()
    
        # DELET OLD FILES
        for path in glob(os.path.join(self.path_protobufs, '*.pbf')): os.system(f"rm -f {path}")
    
    def Spliter(self, DF_GEOPANDAS, ncut: int = 1):
        """
        Divide uma geometria em várias partes com base em um número de divisões (ncut).
        
        Parameters:
            DF_GEOPANDAS (GeoDataFrame): Geometria carregada pelo GeoPandas.
            ncut (int): Número de cortes (subdivisões) ao longo de cada eixo (x e y).

        Returns:
            dict: Um dicionário onde as chaves são os índices dos cortes e os valores são
                os subconjuntos das geometrias cortadas.
        """
        
        # Obter a bounding box da geometria
        bounds = DF_GEOPANDAS.total_bounds  # xmin, ymin, xmax, ymax
        xmin, ymin, xmax, ymax = bounds

        # Calcular o tamanho de cada subdivisão
        step_x = (xmax - xmin) / ncut

        # Dicionário para armazenar os recortes
        split_geometries = {}

        # Criar divisões usando bbox
        for i in range(ncut):
            bbox = Polygon([
                (xmin + i * step_x, ymin),  # Bottom-left
                (xmin + (i + 1) * step_x, ymin),  # Bottom-right
                (xmin + (i + 1) * step_x, ymax),  # Top-right
                (xmin + i * step_x, ymax),  # Top-left
                (xmin + i * step_x, ymin),  # Closing the loop
            ])
            
            # Recortar a geometria original usando a bbox
            clipped = gpd.clip(DF_GEOPANDAS, bbox)

            # Adicionar ao dicionário se houver geometrias na subdivisão
            if not clipped.empty: split_geometries[i] = clipped

        return split_geometries
    
    def _GetGeojsonUFs(self):
        return glob(self.PathGeoJsons)
    
    def _GetProtobuf(self):
        """
        Função sempre irá usar o maior protobuf, preferencia deixe o do proto
        do pais todo.
        """
        path_bufs = glob(os.path.join(self.path_protobuf, "*.pbf"))
        if len(path_bufs) == 0: raise Exception("Pasta do Protobuf Vazia, baixe o no Geofabrik e insira na mesma.")
        if len(path_bufs) > 1: raise Warning(f"Lembre-se de manter somente um arquivo na pata {self.path_protobuf}, será processado somente o protobuf maior.")
        return max([[protobuf, os.path.getsize(protobuf)] for protobuf in glob(os.path.join(self.path_protobuf, "*.pbf"))], key=lambda x: x[1])[0]
    
    def _get_types(self):
        with open(os.path.join('osm2pgrouting', configRun["TYPE_MAP_OSM"]), 'r') as f:
            data = f.read()
        Bs_data = BeautifulSoup(data, "xml")
        all_tags = {}
        for tag in Bs_data.find_all('tag_name'):
            name = tag.get('name')
            all_tags[name] = []
            for value in tag.find_all('tag_value'):
                all_tags[name].append(value.get('name'))
        return all_tags
    
    def _pre_run(self):
        path_Protobuf = self._GetProtobuf()
        base_path_tagbuf = os.path.join(os.path.dirname(path_Protobuf), "TAGBUF")
        os.makedirs(base_path_tagbuf, exist_ok=True)
        for path in glob(os.path.join(base_path_tagbuf, '*.*')): os.system(f"rm -f {path}")
        path_protofile =os.path.join(os.path.dirname(path_Protobuf), "TAGBUF", "tag-filter-"+os.path.basename(path_Protobuf))
        mytypes = " ".join([(f"w/{tag_name}="+",".join(tags_value)) for tag_name, tags_value in self._get_types().items()]).strip()
        run = f"osmium tags-filter {path_Protobuf} {mytypes} --overwrite -o {path_protofile}".replace("\\","/").strip()
        print(f"\nTAG-FILTER: {run}")
        result = subprocess.run(run.split(' '), capture_output=True, text=True, check=True)
        print(result.stdout)
        print(result.stderr)
        time.sleep(2)
        return path_protofile if os.path.exists(path_protofile) else None
    
    def run(self):
        path_UFs            = self._GetGeojsonUFs()
        path_Protobuf       = self._GetProtobuf()
        path_protofile_pr   = self._pre_run()
        path_Protobuf = path_Protobuf if path_protofile_pr == None else path_protofile_pr
        for GeojsonUF in path_UFs:
            out_file_name = os.path.splitext(os.path.basename(GeojsonUF))[0]
            path_protofile=f'PROTOBUF/PROTOBUFs/{out_file_name}.pbf'
            os.system(f"chmod +x {GeojsonUF}")
            os.system(f"chmod +x {path_Protobuf}")
            run = f"osmium extract -p {GeojsonUF} {path_Protobuf} --overwrite -o {path_protofile}".replace("\\","/").strip()
            print(f"\nSPLITING: {run}")
            result = subprocess.run(run.split(' '), capture_output=True, text=True, check=True)
            print(result.stdout)
            print(result.stderr)
            if os.path.exists(path_protofile):
                os.system(f"chmod +x {path_protofile}")
                filesize = (os.path.getsize(path_protofile)/1024)/1024
                if filesize >= configRun["SIZELIMIT"] and configRun["SIZELIMIT"] > 0:
                    self.keys_reprocess[out_file_name] = {"PATHGEOJSON": GeojsonUF, "FILESIZE": filesize, "PATHBUF": path_protofile, "ORIGINBUF": path_protofile}
        if len(list(self.keys_reprocess.items())) > 0:
            self._Reprocess()
    
    def _Reprocess(self):
        for key, value in self.keys_reprocess.items():
            ncut            = math.ceil(value["FILESIZE"]/configRun["SIZELIMIT"]) 
            DF_GEOPANDAS    = gpd.read_file(value["PATHGEOJSON"])
            DictSpliter     = self.Spliter(DF_GEOPANDAS, ncut=ncut)
            for partition, value2   in DictSpliter.items():
                DF_GEOPANDAS_SPLITED    = value2
                GeojsonUFSplited        = os.path.join(os.path.join(os.path.dirname(value["PATHGEOJSON"]),  (key + "-Part" + str(partition)) + ".geojson"))
                path_protofile          = os.path.join(os.path.join(os.path.dirname(value["PATHBUF"]),      (key + "-Part" + str(partition)) + ".pbf"))
                DF_GEOPANDAS_SPLITED.to_file(GeojsonUFSplited, driver='GeoJSON')
                run = f"osmium extract -p {GeojsonUFSplited} {value['ORIGINBUF']} --overwrite --verbose -o {path_protofile}".replace("\\","/").strip()
                print(f"\nRE-SPLITING: {run}")
                result = subprocess.run(run.split(' '), capture_output=True, text=True, check=True)
                print(result.stdout)
                print(result.stderr)
            os.system(f"rm -f {value['PATHGEOJSON']}")
            os.system(f"rm -f {value['PATHBUF']}")