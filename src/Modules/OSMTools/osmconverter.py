from Modules.Config.env import configRun
from glob import glob
import subprocess
import os

class OSMConverter:
    
    def __init__(self):
        self.base_path      = 'Modules'
        self.folder_module  = 'OSMTools'
        self.folder_bin     = 'bin'
        self.filename_bin   = 'osmconvert64'
        
        self.path_protobufs = os.path.join("PROTOBUF", "PROTOBUFs")
        self.path_bin       = os.path.join(self.base_path, self.folder_module, self.folder_bin, self.filename_bin)
    
        # DELET OLD FILES
        for path in glob(os.path.join(configRun["PATHSAVE"], '*.osm')): os.system(f"rm -f {path}")
    
    def _get_protobufs(self):
        return glob(os.path.join(self.path_protobufs, "*.pbf"))
        
    def run(self):
        # os.system(f"chmod +x ./{self.path_bin}")
        for path_protobuf in self._get_protobufs():
            out_file_name = os.path.join(configRun["PATHSAVE"],f"{os.path.splitext(os.path.basename(path_protobuf))[0]}.osm")
            run = f"./{self.path_bin} {path_protobuf} --drop-author --drop-version --complete-ways --complete-multipolygons -o={out_file_name}"
            print(f"\nCONVERTER: {run}")
            result = subprocess.run(run.split(' '), capture_output=True, text=True, check=True)
            print(result.stdout)
            print(result.stderr)