# NGF or BDNF? Telling Two Growth Factors Apart from Single-Neuron Signaling Profiles

DS 4021 final project. Group members: Timothy Lee, Nathan Myers.

**Research question:** Can machine-learning models tell apart rat sympathetic neurons stimulated for 30 minutes with NGF from those stimulated with BDNF using only their single-cell signaling profiles?

The data come from an unpublished imaging mass cytometry (IMC) experiment on cultured rat superior cervical ganglion (SCG) cells. This project uses two of the experiment's five treatments: 30-minute NGF (`N`) and 30-minute BDNF (`B`). See [CLAUDE.md](CLAUDE.md) for the full experiment, marker panel and data notes.

## Repository contents

### Software and platform

| Item | Version |
|---|---|
| Python | 3.13.9 (Anaconda) |
| Jupyter notebooks | JupyterLab / Notebook |
| Packages | pandas, numpy, scikit-learn, matplotlib, seaborn, PyTorch; tifffile, scipy, scikit-image (only for `scripts/build_cell_table.py`) |
| Operating system | macOS 15.7 |

### Map of the repository

```
.
├── README.md
├── CLAUDE.md                     dataset handoff notes (experiment, markers, caveats)
├── final_report.pdf              (added at the end)
├── scripts/
│   └── build_cell_table.py       builds the two CSVs below from the raw images and masks
├── Data/
│   ├── reporting_set.csv         20% held-out set (2 whole images) — DO NOT TOUCH until the final evaluation
│   ├── training_set.csv          remaining 80% (8 images)
│   ├── split_rois.csv            which image went to which set
│   └── raw/
│       ├── metadata/
│       │   ├── fov_annotation.csv   one row per image (ROI): treatment, well, laser setting, image filename
│       │   ├── panel.csv            the 57 image channels in TIFF order
│       │   └── manifest.csv         ROI → mask file → source TIFF
│       ├── masks/                   16 NGF/BDNF segmentation masks (one per ROI, 1000×1000, uint32 labels)
│       ├── neuron_labels/
│       │   └── cell_neuron_assignments.csv   Well 1 neuron/non-neuron labels from the lab's gate
│       └── images/                  raw 57-channel TIFFs (local only, not in GitHub — see below)
├── NOTEBOOKS/
│   ├── 01_descriptive_analysis.ipynb
│   ├── 02_student1_<models>.ipynb
│   ├── 03_student2_pytorch_nn.ipynb
│   └── 04_final_reporting_set_evaluation.ipynb
└── OUTPUT/                       figures and tables
```

The `mask_file` paths in `manifest.csv` are relative to `Data/raw/`. `manifest.csv` and `fov_annotation.csv` still list all 40 ROIs; only the NGF/BDNF masks are kept here.

**Raw images:** the 40 TIFFs (~217 MB each, 8.5 GB total) are too large for GitHub and are gitignored. Download them from [Google Drive](https://drive.google.com/drive/folders/1uI9Ybl1xGFKAJdR3-ZetKnKaAUxBWbwJ) into `Data/raw/images/` only if you want to rebuild the CSVs. The modeling notebooks only need `Data/training_set.csv` and `Data/reporting_set.csv`.

### Datasets

Built by `python scripts/build_cell_table.py` (about 10 seconds; it needs the raw images).

- **Rows:** one per gate-passing neuron in Well 1 of the 30-minute NGF (`N`) and BDNF (`B`) treatments. That is 3,360 neurons from 10 images. Well 2 has no neuron labels, so it is not used.
- **Split:** one NGF and one BDNF image are held out with a fixed seed (4021): `B_1_04` and `N_1_05`. That gives 672 reporting neurons (20.0%, 47.8% BDNF) and 2,688 training neurons (8 images, 56.7% BDNF).
- **Target:** `y` = 1 for BDNF, 0 for NGF (`treatment` holds the same information as text).
- **ID columns, not features:** `cell_id` (`<ROI>:<mask_label>`, traceable back to the image), `roi` (use as the group for cross-validation), `treatment`, `well`, `mask_label`, `centroid_x`, `centroid_y`.
- **Features (34):**
  - Mean intensity inside the nucleus mask (`_nuc`) and in a 3 µm ring around it (`_ring`) for Tuj1, H3K9ac, p-Akt S473, p-PLCγ2, p-Tyr, p-S6, c-Fos, p-ATM, TrkA, p-NFκB, p-Akt T308, p-CREB and Ir191.
  - Nucleus shape: `area_um2`, `perimeter`, `eccentricity`, `solidity`, `major_axis_length`, `minor_axis_length`.
  - Crowding: `n_neighbors_50um` and `nearest_neighbor_um`, counted over all segmented cells, not only neurons.
- **Left out on purpose:** TH, Ret and p75NTR, because the neuron gate used per-treatment cutoffs on them and they would leak the label. p-c-Jun and cleaved caspase-3 are left out because they are unreliable in this experiment.
- **Missing values:** 59 training neurons have no free ring pixels because they are fully surrounded by other cells, so their 13 `_ring` columns are empty. Impute them inside the cross-validation pipeline.
- **Raw intensities:** values are raw ion counts with no transform. They are heavily right-skewed, so apply `arcsinh` (or `log1p`) inside the pipeline.

Check your models' CV performance against chance. Near-chance ROC-AUC is a valid result.

### Group member responsibilities

Group of two, following the Individual Component rubric:

| Member | Modeling task | Notebook |
|---|---|---|
| Nathan Myers | Student 1: penalized logistic regression (or SVM) AND random forest (or gradient boosting) — state which | `NOTEBOOKS/02_student1_<models>.ipynb` |
| Timothy Lee | Student 2: neural network in PyTorch | `NOTEBOOKS/03_student2_pytorch_nn.ipynb` |

Both members use the same `training_set.csv`, the same cross-validation folds (grouped by image) and the same primary metric (ROC-AUC) so the models can be compared fairly.
