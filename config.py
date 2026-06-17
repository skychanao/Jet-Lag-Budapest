import os
import logging
from pathlib import Path

# Base folder for resources
SCRIPT_FOLDER = Path(__file__).parent / "input"

def setup_environment():
    """Setup OS and logging variables."""
    # OS stuff
    os.environ['CPL_LOG'] = 'NUL'
    os.environ['CPL_LOG_ERRORS'] = 'OFF'    

    # Streamlit Remove warning
    logging.getLogger('fiona').setLevel(logging.ERROR)
    logging.getLogger('fiona.ogrext').setLevel(logging.ERROR)
    logging.getLogger('GDAL').setLevel(logging.ERROR)
    logging.getLogger('rasterio').setLevel(logging.ERROR)
