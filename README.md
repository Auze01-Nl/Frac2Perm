# Frac2Perm

Fracture network modeling and P21-based permeability and P-wave (Vp) analysis in Python.

---

## Required Python libraries

Install the required packages:

pip install numpy pandas matplotlib scipy shapely

---

## Main Pipeline (main.py)

The main.py script is the entry point of the Frac2Perm workflow.

It runs the full processing chain from raw fracture data to final physical and seismic outputs.

---

## What the pipeline does

1. Load input data

fracture_data.csv (mandatory)
- Must contain 4 columns in this order:
  - x-coordinate
  - y-coordinate
  - z-coordinate
  - polyline_id
- Column names are ignored (only order matters)

vp_data.csv (optional)
- Seismic velocity data (Vp cloud)

porosity_data.csv (optional)
- Porosity cloud data

---

2. Preprocessing
- Standardizes fracture format
- Ensures consistent coordinate structure

---

3. Fracture network construction
- Splits polylines into segments
- Detects geometric intersections
- Builds a connected fracture network

---

4. Topology analysis
- Extracts fracture nodes
- Classifies connectivity:
  - i → isolated nodes
  - y → Y-junctions
  - x → cross / multi-junctions

---

5. P21 & physical properties computation
- Computes P21 fracture intensity
- Estimates permeability tensors (kxx, kzz)
- Builds effective porosity field

---

6. Visualization
- P21 maps
- Permeability maps
- Porosity distribution
- Seismic Vp field with fractures
- Cross-analysis (Vp vs P21 colored by porosity)

---

## How to run

python main.py



## 📂 Example input files

The repository includes example datasets to test the pipeline.

### 1. fracture_data.csv (mandatory)
This file defines the fracture network.

Format (column order matters):
x, y, z, polyline_id

Each row is a point belonging to a fracture polyline.
All points with the same polyline_id belong to the same fracture.

Each fracture is defined by at least 2 points.

---

### 2. vp_data.csv (optional)
Contains seismic P-wave velocity data.

Format:
x, y, z, vp

Used for seismic interpolation and Vp analysis.

If not provided, seismic plotting will be skipped.

---

### 3. porosity_data.csv (optional)
Contains matrix porosity values.

Format:
x, y, z, porosity

Used to build spatial porosity fields.

If not provided, a default constant porosity field (0.05) is used.
