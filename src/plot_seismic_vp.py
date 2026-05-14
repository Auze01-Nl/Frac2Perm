import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata


def plot_seismic_vp(
        data_seismic,
        df_fracture,
        P21,
        effective_porosity,
        x_start, x_last,
        z_start, z_last,
        linescale=1.0):

    # ============================================================
    # SEISMIC DATA
    # ============================================================
    x = data_seismic.iloc[:, 0].values
    z = data_seismic.iloc[:, 2].values
    vp = data_seismic.iloc[:, 3].values

    # remove first row (same as MATLAB)
    x = x[1:]
    z = z[1:]
    vp = vp[1:]

    # ============================================================
    # INTERPOLATION GRID
    # ============================================================
    xq = np.linspace(np.min(x), np.max(x), 100)
    zq = np.linspace(np.min(z), np.max(z), 100)

    Xq, Zq = np.meshgrid(xq, zq)

    # ============================================================
    # INTERPOLATE VP
    # ============================================================
    Vq = griddata(
        (x, z),
        vp,
        (Xq, Zq),
        method="linear"
    )

    # fill NaNs
    mask = np.isnan(Vq)

    if np.any(mask):
        Vq[mask] = np.nanmean(Vq)

    # ============================================================
    # SAFE fracture access
    # ============================================================
    def get_x1(r):
        return r["x1"] if "x1" in r else r["x"]

    def get_x2(r):
        return r["x2"] if "x2" in r else r["x_prime"]

    def get_z1(r):
        return r["z1"] if "z1" in r else r["z"]

    def get_z2(r):
        return r["z2"] if "z2" in r else r["z_prime"]

    # ============================================================
    # FIGURE 1 — SEISMIC + FRACTURES
    # ============================================================
    fig1, ax1 = plt.subplots(figsize=(12, 9))

    im = ax1.imshow(
        Vq,
        origin="lower",
        extent=[xq.min(), xq.max(), zq.min(), zq.max()],
        aspect="equal",
        cmap="jet",
        vmin=0,
        vmax=5500
    )

    # MATLAB-like colorbar
    cbar = plt.colorbar(
        im,
        ax=ax1,
        fraction=0.015,
        pad=0.018
    )

    cbar.ax.tick_params(labelsize=10)
    cbar.set_label("Vp (m/s)")

    # ------------------------------------------------------------
    # fractures overlay
    # ------------------------------------------------------------
    for _, r in df_fracture.iterrows():

        xx1 = get_x1(r)
        xx2 = get_x2(r)

        zz1 = get_z1(r)
        zz2 = get_z2(r)

        # crop outside fractures
        if (max(xx1, xx2) < x_start or
            min(xx1, xx2) > x_last or
            max(zz1, zz2) < z_start or
            min(zz1, zz2) > z_last):
            continue

        ax1.plot(
            [xx1, xx2],
            [zz1, zz2],
            color="black",
            linewidth=linescale
        )

    # ============================================================
    # AXIS SETTINGS
    # ============================================================
    ax1.set_xlim(x_start, x_last)
    ax1.set_ylim(z_start, z_last)

    ax1.set_xticks(np.arange(x_start, x_last + 1, 1))
    ax1.set_yticks(np.arange(z_start, z_last + 1, 1))

    ax1.tick_params(axis='x', rotation=45)
    ax1.tick_params(axis='y', rotation=45)

    ax1.set_xlabel("X")
    ax1.set_ylabel("Z")

    ax1.set_title("Fractures and Seismic Vp")

    ax1.grid(True)

    # ============================================================
    # INTERPOLATE VP ONTO P21 GRID
    # ============================================================
    x_p21, z_p21 = np.meshgrid(
        np.linspace(x_start, x_last, P21.shape[1]),
        np.linspace(z_start, z_last, P21.shape[0])
    )

    Vp_interp = griddata(
        (Xq.flatten(), Zq.flatten()),
        Vq.flatten(),
        (x_p21, z_p21),
        method="linear"
    )

    # ============================================================
    # FIGURE 2 — VP vs P21
    # ============================================================
    fig2, ax2 = plt.subplots(figsize=(12, 9))

    sc = ax2.scatter(
        P21.flatten(),
        Vp_interp.flatten(),
        s=40,
        c=effective_porosity.flatten(),
        cmap="jet"
    )

    cbar2 = plt.colorbar(
        sc,
        ax=ax2,
        fraction=0.015,
        pad=0.018
    )

    cbar2.ax.tick_params(labelsize=10)
    cbar2.set_label("Porosity (%)")

    ax2.set_xlabel("P21 (m$^{-1}$)")
    ax2.set_ylabel("Vp (m/s)")

    ax2.set_title("Vp vs P21 colored by Porosity")

    ax2.grid(True)
    print("ALL DONE", flush=True)

    plt.tight_layout()
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)