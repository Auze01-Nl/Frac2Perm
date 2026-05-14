# Frac2Perm
Fracture network modeling and P21-based permeability and p-wave (vp) analysis in Python.

### 🔧 Required Python libraries

Before running the code, make sure the following packages are installed:

```bash
pip install numpy pandas matplotlib scipy

Main Pipeline (main.py)

The main.py script is the entry point of the Frac2Perm workflow.

It runs the full processing chain from raw fracture data to final physical and seismic outputs.

###  Main ⚙️ What the pipeline does
1. Load input data
  fracture_data.csv (mandatory)
  Must contain at least 4 columns (order matters):
  x-coordinate
  y-coordinate
  z-coordinate
  polyline_id
  Column names are ignored
  vp_data.csv (optional)
  porosity_data.csv (optional)
2. Preprocessing
  Standardizes fracture format
  Ensures consistent coordinate structure
3. Fracture network construction
  Splits polylines into segments
  Detects geometric intersections
  Builds connected fracture network
4. Topology analysis
  Extracts fracture nodes
  Classifies connectivity:
  i → isolated nodes
  y → Y-junctions
  x → cross / multi-junctions
5. P21 & physical properties computation
  Computes P21 fracture intensity
  Estimates permeability tensors (kxx, kzz)
  Builds effective porosity field
6. Visualization
  P21 maps
  Permeability maps
  Porosity distribution
  Seismic Vp field with fracture overlay
  Cross-analysis (Vp vs P21 colored by porosity)

▶️ How to run
python main.py
