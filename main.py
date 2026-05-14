


# =====================================================
# LOAD DATA
# =====================================================
import os
os.chdir(r"C:\Users\Antoine\Desktop\Frac2PERM_py") # here put the path of the Frac2PERM_py folder

# =====================================================
# INPUT FILES
# =====================================================
file_fracture = "fracture_data.csv" # mandatory here put you x y z name, fracture polylines  file 
file_seismic = "vp_data.csv"  # optional here put you x y z vp,  cloud file, if none, write "0"
file_porosity = "porosity_data.csv" # optional here put you x y z porosity, cloud file




# =====================================================
# GRID
# =====================================================
x_start, x_last = 598462, 598476.5        # first and last x coordinates (m)
z_start, z_last = 112, 116                # first and last z elevation coordinates or y if from the top view (m)

size_grid_x = 0.5     # grid size for p21 , porosity interpolation and seismic
size_grid_z = 0.5                         

num_x = int((x_last - x_start) / size_grid_x)
num_z = int((z_last - z_start) / size_grid_z)

increment_x = size_grid_x
increment_z = size_grid_z

# =====================================================
# START CODE
# =====================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

plt.close("all")



data = pd.read_csv("fracture_data.csv") 

if os.path.exists(file_porosity):
    porosity_data = pd.read_csv(file_porosity)
    print("Porosity loaded")
else:
    print("No porosity file → using default 0.05 field")

    porosity_data = pd.DataFrame({
        "x": data["x"],
        "y": data["y"],
        "z": data["z"],
        "porosity": 0.05
    })

if os.path.exists(file_seismic):
    data_seismic = pd.read_csv(file_seismic)
    print("Seismic loaded")
else:
    data_seismic = None
    print("No seismic file → skipping seismic analysis")


# =====================================================
# IMPORT PIPELINE
# =====================================================
from src.preprocessing import preprocess_polylines
from src.make_data_fracture import make_data_fracture
from src.make_Topology_fractures import make_Topology_fractures
from src.make_P21 import run_all
from src.plot_P21_all import plot_P21_all
from src.plot_seismic_vp import plot_seismic_vp

# =====================================================
# RUN PIPELINE
# =====================================================
print("START PIPELINE", flush=True)

print("Grid:", num_x, num_z, flush=True)

# 1. preprocess
data = preprocess_polylines(data)
print("Preprocessing DONE", flush=True)

# 2. fractures
data_clean, data_fracture, intersection_nodes = make_data_fracture(data)
print("Fractures built", flush=True)

# 3. topology
data_fracture, nodes_topology = make_Topology_fractures(
    data_fracture,
    threshold=0.05,
    x_start=x_start,
    x_last=x_last,
    z_start=z_start,
    z_last=z_last,
    linescale=1.0
)
print("Topology DONE", flush=True)

# 4. P21 model
df_out, P21, kxx, kzz, kxz, porosity, x_scale, z_scale = run_all(
    data_fracture,
    x_start=x_start,
    z_start=z_start,
    dx=increment_x,
    dz=increment_z,
    num_x=num_x,
    num_z=num_z,
    x_last=x_last,
    z_last=z_last,
    porosity_data=porosity_data
)

print("P21 FINISHED", flush=True)

# =====================================================
# PLOT SECTION
# =====================================================
print("Starting plots...", flush=True)

plot_P21_all(
    P21=P21,
    kxx=kxx,
    kzz=kzz,
    porosity=porosity,
    x_start=x_start,
    x_last=x_last,
    z_start=z_start,
    z_last=z_last,
    df=data_fracture,
    linescale=1.0
)

print("P21 plots DONE", flush=True)


if data_seismic is not None:
    plot_seismic_vp(
        data_seismic=data_seismic,
        df_fracture=data_fracture,
        P21=P21,
        effective_porosity=porosity,
        x_start=x_start,
        x_last=x_last,
        z_start=z_start,
        z_last=z_last,
        linescale=1.0
    )
else:
    print("Skipping seismic plot (no seismic data)")


plt.show(block=True)
