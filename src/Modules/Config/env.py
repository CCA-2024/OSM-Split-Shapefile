from dotenv import load_dotenv
import os

load_dotenv()

confiRun       = {
    "SIZELIMIT":               eval(os.getenv("SIZELIMIT")),
}