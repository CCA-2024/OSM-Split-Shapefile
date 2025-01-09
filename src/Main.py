from Modules.OSMTools.osmsplit      import OSMSplit
from Modules.OSMTools.osmconverter  import OSMConverter

# RECORTANDO PROTOBUFs
SplitTool       = OSMSplit()
SplitTool.run()

# CONVERTENDO *PBF TO *.OSM
ConverterTool   = OSMConverter()
ConverterTool.run()