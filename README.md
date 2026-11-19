# NGF or BDNF? Telling Two Growth Factors Apart from Single-Neuron Signaling Profiles

DS 4021 final project. Group members: Name 1, Name 2.

**Research question:** Can machine-learning models tell apart rat sympathetic neurons stimulated for 30 minutes with NGF from those stimulated with BDNF using only their single-cell signaling profiles?

The data come from an unpublished imaging mass cytometry (IMC) experiment on cultured rat superior cervical ganglion (SCG) cells. This project uses two of the experiment's five treatments: 30-minute NGF (`N`) and 30-minute BDNF (`B`). See [CLAUDE.md](CLAUDE.md) for the full experiment, marker panel and data notes.

## Repository contents

### Software and platform

| Item | Version |
|---|---|
| Python | 3.x (fill in) |
| Jupyter notebooks | JupyterLab / Notebook |
| Packages | pandas, numpy, scikit-learn, matplotlib, seaborn, PyTorch, tifffile |
| Operating system | macOS (fill in version) |

### Map of the repository

```
.
├── README.md
├── CLAUDE.md                     dataset handoff notes (experiment, markers, caveats)
├── final_report.pdf              (added at the end)
├── Data/
│   ├── reporting_set.csv         20% held-out set (whole images) — DO NOT TOUCH until the final evaluation
│   ├── training_set.csv          remaining 80%
│   └── raw/
│       ├── metadata/
│       │   ├── fov_annotation.csv   one row per image (ROI): treatment, well, laser setting, image filename
│       │   ├── panel.csv            the 57 image channels in TIFF order
│       │   └── manifest.csv         ROI → mask file → source TIFF
│       ├── masks/                   40 segmentation masks (one per ROI, 1000×1000, uint32 labels)
│       ├── neuron_labels/
│       │   ├── cell_neuron_assignments.csv   Well 1 neuron/non-neuron labels from the lab's gate
│       │   └── condition_thresholds.csv      TH/Ret/p75NTR cutoffs used per treatment
│       └── images/                  raw 57-channel TIFFs (local only, not in GitHub — see below)
├── NOTEBOOKS/
│   ├── 01_descriptive_analysis.ipynb
│   ├── 02_student1_<models>.ipynb
│   ├── 03_student2_pytorch_nn.ipynb
│   └── 04_final_reporting_set_evaluation.ipynb
└── OUTPUT/                       figures and tables
```

`Data/reporting_set.csv` and `Data/training_set.csv` are added once the cell table is built. The `mask_file` paths in `manifest.csv` are relative to `Data/raw/`.

**Raw images:** the 40 TIFFs (~217 MB each, 8.5 GB total) are too large for GitHub and are gitignored. Download them from the Google Drive link (fill in) into `Data/raw/images/` to rebuild the cell table.

### Group member responsibilities

Group of two, following the Individual Component rubric:

| Member | Modeling task | Notebook |
|---|---|---|
| Name 1 | Student 1: penalized logistic regression (or SVM) AND random forest (or gradient boosting) — state which | `NOTEBOOKS/02_student1_<models>.ipynb` |
| Name 2 | Student 2: neural network in PyTorch | `NOTEBOOKS/03_student2_pytorch_nn.ipynb` |

Both members use the same `training_set.csv`, the same cross-validation folds (grouped by image) and the same primary metric (ROC-AUC) so the models can be compared fairly.
