import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt


def plot_P21_all(P21, kxx, kzz, porosity,
                 x_start, x_last,
                 z_start, z_last,
                 df,
                 linescale=1.0):

    # ============================================================
    # GRID EXTENT
    # ============================================================
    extent = [x_start, x_last, z_start, z_last]

    # ============================================================
    # SAFE fracture coordinate access
    # supports:
    # x1/x2/z1/z2
    # OR
    # x/x_prime/z/z_prime
    # ============================================================
    def x1(r):
        return r["x1"] if "x1" in r else r["x"]

    def x2(r):
        return r["x2"] if "x2" in r else r["x_prime"]

    def z1(r):
        return r["z1"] if "z1" in r else r["z"]

    def z2(r):
        return r["z2"] if "z2" in r else r["z_prime"]

    # ============================================================
    # GENERIC FIELD PLOTTER
    # ============================================================
    def plot_field(ax,
                   field,
                   title,
                   cmap="jet",
                   vmin=None,
                   vmax=None):

        im = ax.imshow(
            field,
            origin="lower",
            extent=extent,
            aspect="equal",
            cmap=cmap,
            vmin=vmin,
            vmax=vmax
        )

        # --------------------------------------------------------
        # SMALL MATLAB-LIKE COLORBAR
        # --------------------------------------------------------
        cbar = plt.colorbar(
            im,
            ax=ax,
            fraction=0.015,
            pad=0.018
        )

        cbar.ax.tick_params(labelsize=10)

        # --------------------------------------------------------
        # FRACTURE OVERLAY
        # --------------------------------------------------------
        for _, r in df.iterrows():

            xx1 = x1(r)
            xx2 = x2(r)

            zz1 = z1(r)
            zz2 = z2(r)

            # crop fractures outside view
            if (max(xx1, xx2) < x_start or
                min(xx1, xx2) > x_last or
                max(zz1, zz2) < z_start or
                min(zz1, zz2) > z_last):
                continue

            ax.plot(
                [xx1, xx2],
                [zz1, zz2],
                color="black",
                linewidth=linescale
            )

        # --------------------------------------------------------
        # AXIS SETTINGS
        # --------------------------------------------------------
        ax.set_xlim(x_start, x_last)
        ax.set_ylim(z_start, z_last)

        ax.set_xticks(np.arange(x_start, x_last + 1, 1))
        ax.set_yticks(np.arange(z_start, z_last + 1, 1))

        ax.tick_params(axis='x', rotation=45)
        ax.tick_params(axis='y', rotation=45)

        ax.grid(False)

        ax.set_title(title, fontsize=16)
        ax.set_xlabel("X")
        ax.set_ylabel("Z")

    # ============================================================
    # FIGURE 1 — P21
    # ============================================================
    fig1, ax1 = plt.subplots(figsize=(12, 9))

    plot_field(
        ax1,
        P21,
        "P21 (m-1)",
        cmap="viridis"
    )

    # ============================================================
    # FIGURE 2 — kxx
    # ============================================================
    fig2, ax2 = plt.subplots(figsize=(12, 9))

    plot_field(
        ax2,
        kxx,
        "kxx (m2)",
       cmap="plasma",
    )

    # ============================================================
    # FIGURE 3 — kzz
    # ============================================================
    fig3, ax3 = plt.subplots(figsize=(12, 9))

    plot_field(
        ax3,
        kzz,
        "kzz (m2)",
        cmap="plasma",
    )

    # ============================================================
    # FIGURE 4 — POROSITY
    # ============================================================
    fig4, ax4 = plt.subplots(figsize=(12, 9))

    plot_field(
        ax4,
        porosity,
        "Porosity (%)",
        cmap="cividis",
        vmin=0,
        vmax=18
    )

    # ============================================================
    # FINAL DISPLAY
    # ============================================================
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)