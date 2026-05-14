import pandas as pd
import numpy as np
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree



def make_data_fracture(data: pd.DataFrame):
    """
    Build a fracture network from polyline data by detecting intersections
    and splitting segments at intersection points.

    The function converts raw fracture polylines into a consistent segmented
    network where intersections are explicitly represented.

    Steps:
    1. Split polylines into line segments
    2. Detect geometric intersections (using STRtree)
    3. Insert intersection points into segments
    4. Split segments at those points to form a connected network

    Parameters
    ----------
    data : pd.DataFrame
        Fracture data with columns [x, y, z, polyline_id]

    Returns
    -------
    data : pd.DataFrame
        Cleaned input data

    data_fracture : pd.DataFrame
        Segmented fractures [polyline_id, x1, z1, x2, z2]

    intersection_nodes : pd.DataFrame
        Unique intersection points [x, z]

    Notes
    -----
    - Intersections are computed in the x–z plane
    - Output represents a graph-like fracture network
    """

    # ============================================================
    # FIXED: proper indentation (4 spaces)
    # ============================================================
    data = data.copy().reset_index(drop=True)

    # ============================================================
    # 1. BUILD SEGMENTS
    # ============================================================
    segments = []
    seg_info = []

    for pid, group in data.groupby("polyline_id"):
        group = group.reset_index()

        coords = group[["x", "z"]].values
        idxs = group["index"].values

        for i in range(len(coords) - 1):
            segments.append(LineString([coords[i], coords[i + 1]]))
            seg_info.append((pid, idxs[i], idxs[i + 1]))

    n = len(segments)

    # ============================================================
    # 2. SPATIAL INDEX (FAST SEARCH)
    # ============================================================
    tree = STRtree(segments)

    # map geometry id → index
    geom_to_i = {id(g): i for i, g in enumerate(segments)}

    split_points = [set() for _ in range(n)]

    # ============================================================
    # 3. INTERSECTION DETECTION
    # ============================================================
    for i, seg in enumerate(segments):

        for cand in tree.query(seg):

            j = geom_to_i.get(id(cand))
            if j is None or j <= i:
                continue

            ipt = seg.intersection(cand)

            if isinstance(ipt, Point) and not ipt.is_empty:
                p = (round(ipt.x, 9), round(ipt.y, 9))
                split_points[i].add(p)
                split_points[j].add(p)

    # ============================================================
    # 4. SPLIT SEGMENTS
    # ============================================================
    rows = []

    for i, seg in enumerate(segments):

        pid, _, _ = seg_info[i]
        pts = list(split_points[i])

        coords = [seg.coords[0]] + pts + [seg.coords[1]]
        coords = sorted(coords)

        for p1, p2 in zip(coords[:-1], coords[1:]):

            if np.hypot(p1[0] - p2[0], p1[1] - p2[1]) < 1e-12:
                continue

            rows.append([pid, p1[0], p1[1], p2[0], p2[1]])

    data_fracture = pd.DataFrame(
        rows,
        columns=["polyline_id", "x1", "z1", "x2", "z2"]
    )

    # ============================================================
    # 5. INTERSECTION NODES
    # ============================================================
    pts = set()
    for s in split_points:
        pts.update(s)

    intersection_nodes = pd.DataFrame(list(pts), columns=["x", "z"])

    # ============================================================
    # 6. CLEAN IDS
    # ============================================================
    data_fracture["polyline_id"] = (
        pd.factorize(data_fracture["polyline_id"])[0] + 1
    )

    return data, data_fracture, intersection_nodes
