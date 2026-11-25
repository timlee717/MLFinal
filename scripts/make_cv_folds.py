"""Assign the 8 training images to 4 shared cross-validation folds.

Each fold holds out one BDNF image and one NGF image, so every test fold
contains both classes (ROC-AUC is defined) and no image is ever split between
training and testing within a fold.

Reads:   Data/split_rois.csv   (only rows with split == "training" are used)
Writes:  Data/cv_folds.csv     one row per training image: roi, treatment, fold, n_neurons

The reporting-set images are never read or listed here.

Usage (from the repo root):  python scripts/make_cv_folds.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"
SEED = 4021  # same seed as scripts/build_cell_table.py

rois = pd.read_csv(DATA / "split_rois.csv")
train_rois = rois[rois.split == "training"]

# Shuffle the BDNF and NGF images separately, then pair them up by position:
# fold k = (k-th shuffled BDNF image, k-th shuffled NGF image)
rng = np.random.default_rng(SEED)
bdnf = rng.permutation(sorted(train_rois.roi[train_rois.treatment == "B"]))
ngf = rng.permutation(sorted(train_rois.roi[train_rois.treatment == "N"]))
assert len(bdnf) == len(ngf), "need the same number of BDNF and NGF training images"

fold_of = {roi: k for k, pair in enumerate(zip(bdnf, ngf)) for roi in pair}

folds = (train_rois.assign(fold=train_rois.roi.map(fold_of))
         [["roi", "treatment", "fold", "n_neurons"]]
         .sort_values(["fold", "treatment"])
         .reset_index(drop=True))

# Sanity checks: every fold has exactly one image of each class
for k, g in folds.groupby("fold"):
    assert sorted(g.treatment) == ["B", "N"], f"fold {k} is not one BDNF + one NGF image"
assert not rois[rois.split == "reporting"].roi.isin(folds.roi).any()

folds.to_csv(DATA / "cv_folds.csv", index=False)
print(folds.to_string(index=False))
print("\nNeurons held out per fold:")
print(folds.groupby("fold").n_neurons.sum().to_string())
