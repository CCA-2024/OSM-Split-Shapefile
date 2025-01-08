from Modules.UFs.Engine import UFGeo
from glob import glob
import os

class OSMsplit:
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
            
        self.UFProcessor = UFGeo()
        self.PathGeoJsons = self.UFProcessor.execute()
        
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
    
    def run(self):
        path_UFs = self._GetGeojsonUFs()
        path_Protobuf = self._GetProtobuf()
        for GeojsonUF in path_UFs:
            out_file_name = os.path.splitext(os.path.basename(GeojsonUF))[0]
            run = f"osmium extract -p ./{GeojsonUF} {path_Protobuf} --overwrite -o ./PROTOBUF/PROTOBUFs/{out_file_name}.pbf".replace("\\","/").strip()
            os.system(run)