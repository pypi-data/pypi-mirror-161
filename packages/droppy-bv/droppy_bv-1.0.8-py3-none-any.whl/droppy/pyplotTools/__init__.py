from .dfPlot import dfSlider, dfAnimate, dfSurface, dfIsoContour
from .misc import newColorIterator, markerCycle, newMarkerIterator, linestyleCycle, colorCycle
from .misc import newLinestyleIterator, pyplotLegend, autoscale_xy, uniqueLegend
from .misc import getColorMappable, getAngleColorMappable, hexa_to_rgb, rgb_to_hexa, negativeColor
from .misc import align_yaxis, set_tick_format, set_major_format
from .surfacePlot import mapFunction
from ._scatterPlot import kde_scatter, density_scatter, scatterPlot, add_linregress,add_x_y, displayMeanCov
from .mplZoom import ZoomPan
from .meshPlot import plotMesh
from .statPlots import qqplot, qqplot2, distPlot, probN, probN_ci, distPlot_bins, distPlot_bins_pdf, rpPlot
from .addcopyfighandler import copyToClipboard_on
from .concatPlot import readImage, concatPlot
from .geoMap import mapPlot, drawRoute, animRoute, drawMap, standardLon, drawGws, animate_geo_data
from .vtkLUT import vtkLookupTable_from_cmap
from .gnuplot_compat import read_csv_block

from .video_overlay import pictures_2_movie

import os
TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test", "test_data")