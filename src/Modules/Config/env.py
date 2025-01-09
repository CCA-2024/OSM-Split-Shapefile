from dotenv import load_dotenv
import os

load_dotenv()

configRun       = {
    "SIZELIMIT":    eval(str(os.getenv("SIZELIMIT"))),
    "PATHSAVE":     os.getenv("PATHSAVE"),
    "TYPE_MAP_OSM": os.getenv("TYPE_MAP_OSM"),
}