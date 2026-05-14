import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def make_Topology_fractures(
    data_fracture,
    threshold,
    x_start,
    x_last,
    z_start,
    z_last,
    linescale
):
    """
    Compute fracture network topology from node connectivity.

    Nodes are classified based on how many nearby endpoints fall within a
    distance threshold.
    """

    df = data_fracture.copy()

    # ============================================================
    # 1. EXTRACT NODE COORDINATES
    # ============================================================
    start_points = df[["x1", "z1"]].values
    end_points = df[["x2", "z2"]].values

    points = np.vstack((start_points, end_points))
    n_points = len(points)

    # ============================================================
    # 2. COMPUTE NODE CONNECTIVITY
    # ============================================================
    num_nodes = np.zeros(n_points)
    topology = np.empty(n_points, dtype=object)

    for i in range(n_points):

        dx = points[:, 0] - points[i, 0]
        dz = points[:, 1] - points[i, 1]

        distances = np.sqrt(dx**2 + dz**2)

        # count neighbors within threshold (excluding self)
        num_connected = np.sum(distances <= threshold) - 1

        num_nodes[i] = num_connected

        if num_connected == 0:
            topology[i] = "i"   # isolated
        elif num_connected == 1:
            topology[i] = "o"   # open endpoint
        elif num_connected == 2:
            topology[i] = "y"   # Y-junction
        else:
            topology[i] = "x"   # cross / multi-junction

    nodes = pd.DataFrame(points, columns=["x", "z"])
    nodes["num_nodes"] = num_nodes
    nodes["topology"] = topology

    # ============================================================
    # 3. TOPOLOGY STATISTICS
    # ============================================================
    active_nodes = nodes[nodes["topology"] != "o"]
    total = len(active_nodes)

    if total > 0:
        pi = 100 * np.sum(active_nodes["topology"] == "i") / total
        py = 100 * np.sum(active_nodes["topology"] == "y") / total
        px = 100 * np.sum(active_nodes["topology"] == "x") / total
    else:
        pi = py = px = 0

    print(f"Percentage of i: {pi:.2f}%")
    print(f"Percentage of y: {py:.2f}%")
    print(f"Percentage of x: {px:.2f}%")

    # ============================================================
    # 4. VISUALIZATION
    # ============================================================
    plt.figure(figsize=(12, 9))
    plt.grid(True)

    # --- plot nodes by class
    i_nodes = nodes[nodes["topology"] == "i"]
    y_nodes = nodes[nodes["topology"] == "y"]
    x_nodes = nodes[nodes["topology"] == "x"]

    h_i = plt.scatter(i_nodes["x"], i_nodes["z"], c="blue", s=10)
    h_y = plt.scatter(y_nodes["x"], y_nodes["z"], c="green", marker="^", s=10)
    h_x = plt.scatter(x_nodes["x"], x_nodes["z"], c="red", marker="s", s=10)

    # --- plot fractures
    for _, r in df.iterrows():
        plt.plot(
            [r["x1"], r["x2"]],
            [r["z1"], r["z2"]],
            color="black",
            linewidth=linescale
        )

    # ============================================================
    # 5. AXIS FORMATTING
    # ============================================================
    plt.xlabel("X-coordinate")
    plt.ylabel("Z-coordinate")
    plt.title("Fracture Network Topology")

    plt.axis("equal")
    plt.xlim(x_start, x_last)
    plt.ylim(z_start, z_last)

    plt.xticks(np.arange(x_start, x_last + 1, 1))
    plt.yticks(np.arange(z_start, z_last + 1, 1))

    # ============================================================
    # 6. LEGEND
    # ============================================================
    labels = [
        f"i ({pi:.1f}%)",
        f"y ({py:.1f}%)",
        f"x ({px:.1f}%)"
    ]

    plt.legend([h_i, h_y, h_x], labels)

    plt.show(block=False)
    plt.pause(0.1)

    return df, nodes