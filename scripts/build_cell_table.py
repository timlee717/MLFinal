"""Build the NGF-vs-BDNF single-neuron table and split it by image.

Run from the repo root:
    python scripts/build_cell_table.py

Inputs (all under Data/raw/):
    images/*.tiff                     57-channel IMC images (local only, see README)
    masks/*_nuclear_as_WC_mask.tif    DeepCell nuclear masks
    metadata/{fov_annotation,manifest,panel}.csv
    neuron_labels/cell_neuron_assignments.csv   Well 1 neuron gate

Outputs:
    Data/training_set.csv     neurons from the 8 training images
    Data/reporting_set.csv    neurons from the 2 held-out images (do not touch until the end)
    Data/split_rois.csv       which image went to which set

Scope: Well 1 only (the neuron gate exists only for Well 1), treatments N and B.
One row per gate-passing neuron, identified by cell_id = "<ROI>:<mask_label>".

Features left out on purpose:
    TH, Ret, p75NTR   the neuron gate used per-treatment cutoffs on these, so they leak the label
    p-c-Jun, clCasp3  flagged unreliable in this experiment
"""

from pathlib import Path

import numpy as np
import pandas as pd
import tifffile
from scipy.spatial import cKDTree
from skimage.measure import regionprops_table
from skimage.segmentation import expand_labels

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "Data" / "raw"
OUT = ROOT / "Data"

SEED = 4021
TREATMENTS = ["N", "B"]          # y = 1 for BDNF, 0 for NGF
WELL = 1
RING_PX = 3                      # ring width around each nucleus, 1 px = 1 um
NEIGHBOR_RADIUS_UM = 50

# Panel name -> short feature name. Order follows panel.csv.
MARKERS = {
    "89Y_Tuj1": "Tuj1",
    "115In_H3K9ac": "H3K9ac",
    "142Nd_p-Akt (pS473)": "pAkt_S473",
    "144Nd_p-PLCg-2": "pPLCg2",
    "146Nd_p-Tyr": "pTyr",
    "149Sm_p-S6": "pS6",
    "155Gd_c-Fos": "cFos",
    "159Tb_p-ATM": "pATM",
    "165Ho_TrkA": "TrkA",
    "166Er_p-NFkB": "pNFkB",
    "169Tm_p-Akt (pT308)": "pAkt_T308",
    "176Yb_p-CREB": "pCREB",
    "191Ir": "Ir191",
}
EXCLUDED = ["161Dy_p75NTR", "163Dy_TH", "171Yb_Ret", "162Dy_p-c-Jun", "173Yb_clCasp3"]


def label_means(labels, image, n):
    """Mean of image over each label 1..n (NaN where a label has no pixels)."""
    flat = labels.ravel()
    sums = np.bincount(flat, weights=image.ravel(), minlength=n + 1)
    counts = np.bincount(flat, minlength=n + 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (sums / counts)[1:]


def measure_roi(row, panel_names):
    mask = tifffile.imread(RAW / row.mask_file).astype(np.int64)
    img = tifffile.imread(RAW / "images" / row.source_image)
    assert img.shape == (len(panel_names), *mask.shape), (row.roi, img.shape)

    n = int(mask.max())
    ring = expand_labels(mask, distance=RING_PX)
    ring[mask > 0] = 0  # ring = new pixels only

    props = pd.DataFrame(regionprops_table(
        mask,
        properties=("label", "area", "perimeter", "eccentricity", "solidity",
                    "major_axis_length", "minor_axis_length", "centroid"),
    )).rename(columns={"label": "mask_label", "area": "area_um2",
                       "centroid-0": "centroid_y", "centroid-1": "centroid_x"})

    idx = props.mask_label.to_numpy() - 1
    for panel_name, short in MARKERS.items():
        plane = img[panel_names.index(panel_name)]
        props[f"{short}_nuc"] = label_means(mask, plane, n)[idx]
        props[f"{short}_ring"] = label_means(ring, plane, n)[idx]

    # Neighborhood, using every segmented cell in the ROI (not only neurons)
    xy = props[["centroid_x", "centroid_y"]].to_numpy()
    tree = cKDTree(xy)
    props["n_neighbors_50um"] = [len(p) - 1 for p in tree.query_ball_point(xy, NEIGHBOR_RADIUS_UM)]
    props["nearest_neighbor_um"] = tree.query(xy, k=2)[0][:, 1]

    props.insert(0, "roi", row.roi)
    props.insert(0, "cell_id", row.roi + ":" + props.mask_label.astype(str))
    return props


def main():
    panel_names = pd.read_csv(RAW / "metadata" / "panel.csv")["name"].tolist()
    for name in list(MARKERS) + EXCLUDED:
        assert name in panel_names, name

    fov = pd.read_csv(RAW / "metadata" / "fov_annotation.csv", dtype={"roi": str})
    manifest = pd.read_csv(RAW / "metadata" / "manifest.csv")
    rois = fov.merge(manifest[["roi", "source_image", "mask_file"]],
                     left_on="fov", right_on="roi", suffixes=("_num", ""))
    assert (rois.image == rois.source_image).all(), "fov_annotation / manifest image mismatch"
    rois = rois[rois.treatment.isin(TREATMENTS) & (rois.well == WELL)].sort_values("roi")
    print(f"{len(rois)} ROIs: {', '.join(rois.roi)}")

    cells = []
    for row in rois.itertuples():
        df = measure_roi(row, panel_names)
        df.insert(2, "treatment", row.treatment)
        df.insert(3, "well", row.well)
        cells.append(df)
        print(f"  {row.roi}: {len(df)} regions")
    cells = pd.concat(cells, ignore_index=True)

    gate = pd.read_csv(RAW / "neuron_labels" / "cell_neuron_assignments.csv",
                       usecols=["cell_id", "is_neuron"])
    cells = cells.merge(gate, on="cell_id", how="left", validate="one_to_one")
    missing = cells.is_neuron.isna().sum()
    assert missing == 0, f"{missing} regions have no neuron assignment"

    neurons = cells[cells.is_neuron.astype(bool)].drop(columns="is_neuron").copy()
    neurons.insert(4, "y", (neurons.treatment == "B").astype(int))
    print(f"{len(neurons)} neurons out of {len(cells)} regions")

    # Hold out 20% of images: one NGF and one BDNF ROI, chosen with a fixed seed
    rng = np.random.default_rng(SEED)
    held_out = sorted(rng.choice(sorted(rois.roi[rois.treatment == t]), 1)[0] for t in TREATMENTS)
    neurons["split"] = np.where(neurons.roi.isin(held_out), "reporting", "training")

    split = (neurons.groupby(["roi", "treatment", "split"]).size()
             .rename("n_neurons").reset_index())
    split.to_csv(OUT / "split_rois.csv", index=False)

    train = neurons[neurons.split == "training"].drop(columns="split")
    report = neurons[neurons.split == "reporting"].drop(columns="split")
    train.to_csv(OUT / "training_set.csv", index=False)
    report.to_csv(OUT / "reporting_set.csv", index=False)

    print(f"held-out images: {held_out}")
    print(f"training:  {len(train)} neurons, {train.roi.nunique()} images, "
          f"{train.y.mean():.1%} BDNF")
    print(f"reporting: {len(report)} neurons, {report.roi.nunique()} images, "
          f"{report.y.mean():.1%} BDNF ({len(report) / len(neurons):.1%} of neurons)")


if __name__ == "__main__":
    main()
