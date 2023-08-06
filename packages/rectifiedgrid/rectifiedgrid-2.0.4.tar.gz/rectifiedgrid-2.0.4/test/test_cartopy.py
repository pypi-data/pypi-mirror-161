import numpy as np
import cartopy
import cartopy.feature as cpf
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.io.img_tiles as cimgt
from rasterio.enums import Resampling

from matplotlib import pyplot as plt
from matplotlib.ticker import LogFormatter
from matplotlib.colors import Normalize, SymLogNorm, LightSource
import rectifiedgrid as rg

# r = rg.read_raster('../test/data/test.tiff')

# r.plotmap()

# plt.show()