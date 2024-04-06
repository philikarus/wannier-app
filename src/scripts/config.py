import os

import plotly.express as px

# for docker build, change WORK_DIR to /data
WORK_DIR = os.path.expanduser("~")
VASP_COLOR = px.colors.qualitative.Plotly[0]
WANN_COLOR = px.colors.qualitative.Plotly[1]
PROJ_COLOR = "Agsunset"
DIS_WIN_COLOR = px.colors.qualitative.Pastel[1]
FROZ_WIN_COLOR = px.colors.qualitative.Pastel[0]
SYMMLINE_COLOR = px.colors.qualitative.Prism[10]
