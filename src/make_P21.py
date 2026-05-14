import numpy as np
import pandas as pd
from scipy.interpolate import griddata


# ============================================================
# 1. PLUNGE + AZIMUTH + LENGTH
# ============================================================
def compute_plunge(df):
    df = df.copy()

    dx = df["x2"].to_numpy() - df["x1"].to_numpy()
    dz = df["z2"].to_numpy() - df["z1"].to_numpy()

    length = np.sqrt(dx**2 + dz**2)

    plunge = np.degrees(
        np.arcsin(np.divide(dz, length, out=np.zeros_like(dz), where=length > 0))
    )

    azimuth = np.degrees(np.arctan2(dx, 1e-12))

    df["length"] = length
    df["Plunges"] = plunge
    df["Azimuth"] = azimuth

    return df


# ============================================================
# 2. CELL INDEXING
# ============================================================
def assign_cells(df, x_start, z_start, dx, dz):
    df = df.copy()

    df["cell_x1"] = ((df["x1"] - x_start) / dx).astype(int)
    df["cell_x2"] = ((df["x2"] - x_start) / dx).astype(int)

    df["cell_z1"] = ((df["z1"] - z_start) / dz).astype(int)
    df["cell_z2"] = ((df["z2"] - z_start) / dz).astype(int)

    return df


# ============================================================
# 3. P21 CORE MODEL
# ============================================================
def build_p21_fast(
    df,
    num_x, num_z,
    x_start, x_last, z_start, z_last,
    increment_x, increment_z,
    porosity_data,
    mean_mechanical_aperture=1.835e-4
):

    num_x = int(num_x)
    num_z = int(num_z)

    P21 = np.zeros((num_z, num_x))
    kxx = np.zeros((num_z, num_x))
    kzz = np.zeros((num_z, num_x))
    kxz = np.zeros((num_z, num_x))
    length_grid = np.zeros((num_z, num_x))

    kf = 1e-13

    # ========================================================
    # FRACTURE CONTRIBUTION
    # ========================================================
    for _, r in df.iterrows():

        ix_min = int(max(0, min(r.cell_x1, r.cell_x2)))
        ix_max = int(min(num_x - 1, max(r.cell_x1, r.cell_x2)))

        iz_min = int(max(0, min(r.cell_z1, r.cell_z2)))
        iz_max = int(min(num_z - 1, max(r.cell_z1, r.cell_z2)))

        length = r.length
        if length <= 0:
            continue

        c = np.cos(np.radians(r.Plunges))
        s = np.sin(np.radians(r.Plunges))

        for i in range(iz_min, iz_max + 1):
            for j in range(ix_min, ix_max + 1):

                P21[i, j] += length
                length_grid[i, j] += length

                kxx[i, j] += kf * c**2
                kzz[i, j] += kf * s**2
                kxz[i, j] += kf * abs(c * s)

    # ========================================================
    # MATRIX POROSITY (INTERPOLATION)
    # ========================================================
    x_scale = np.linspace(
        x_start + increment_x / 2,
        x_last - increment_x / 2,
        num_x
    )

    z_scale = np.linspace(
        z_start + increment_z / 2,
        z_last - increment_z / 2,
        num_z
    )

    Xc, Zc = np.meshgrid(x_scale, z_scale)

    matrix_porosity = griddata(
        (porosity_data.x, porosity_data.z),
        porosity_data.porosity,
        (Xc, Zc),
        method="linear"
    )

    matrix_porosity[np.isnan(matrix_porosity)] = np.nanmean(matrix_porosity)

    # ========================================================
    # FRACTURE POROSITY
    # ========================================================
    extra_porosity = (
        length_grid * mean_mechanical_aperture
    ) / (increment_x * increment_z)

    effective_porosity = (extra_porosity + matrix_porosity) * 100

    return P21, kxx, kzz, kxz, effective_porosity, x_scale, z_scale


# ============================================================
# 4. FULL PIPELINE WRAPPER
# ============================================================
def run_all(
    df,
    x_start, z_start,
    dx, dz,
    num_x, num_z,
    x_last, z_last,
    porosity_data
):

    df = compute_plunge(df)
    df = assign_cells(df, x_start, z_start, dx, dz)

    P21, kxx, kzz, kxz, porosity, x_scale, z_scale = build_p21_fast(
        df,
        num_x=num_x,
        num_z=num_z,
        x_start=x_start,
        x_last=x_last,
        z_start=z_start,
        z_last=z_last,
        increment_x=dx,
        increment_z=dz,
        porosity_data=porosity_data
    )

    return df, P21, kxx, kzz, kxz, porosity, x_scale, z_scale