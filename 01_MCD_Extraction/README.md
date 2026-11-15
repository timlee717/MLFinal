# MCD extraction — rat SCG culture, 2026-09-08

Source: 40 MCDs in the treatment/Well_1 and treatment/Well_2 folders immediately above this directory.

## Processing

- Steinbock Docker image: ghcr.io/bodenmillergroup/steinbock:0.16.3 (linux/amd64).
- One acquisition per MCD; 1000 × 1000 pixels per acquisition.
- All 57 acquired intensity channels retained; X/Y/Z coordinate fields are not intensity planes.
- Hot-pixel filtering: HPF = 50, applied during extraction.
- Strict MCD parsing; no TXT recovery inputs.
- Original MCDs mounted read-only during extraction.
- No spillover correction, normalization, segmentation, or cell quantification applied.

## Outputs

- `img/`: quantitative multichannel float32 TIFF stacks. Image filenames are the Steinbock-generated names; use the annotation table to map them to treatment/well/ROI.
- `metadata/panel.csv`: channels in TIFF plane order; all keep flags are 1. Unlabeled acquisition channels remain available for diagnostic use. This is an extraction panel, not a final analysis-marker selection.
- `metadata/images.csv`: Steinbock image/acquisition metadata.
- `metadata/fov_annotation.csv`: treatment, well, ROI, laser power, original MCD path, acquisition ID, dimensions, and exported image mapping.
- `metadata/acquired_channels.csv`: original channel names, labels, and acquisition order including coordinates.
- `logs/`: processing scripts, extraction log, per-well image metadata, original file identity/size/time snapshot, channel intensity QC, and validation summary.

## Laser power

User-specified laser power is 1 for Well_1 (25 ROIs) and 2 for Well_2 (15 ROIs).
The embedded MCD AblationPower field is 0 for Well_1 and 1 for Well_2. Both values are retained without assuming how the instrument encodes them. `laser_power_source` records the user-provided provenance.

Well and laser power coincide within each treatment. Preserve both factors for downstream QC and interpretation; their effects cannot be estimated independently from this design.

## Validation

Consult `logs/validation_summary.json` for final completion status. Checks include source acquisition completeness, matching channel schemas, 40 unique exported image records, shape/dtype/finiteness checks on every TIFF, and per-channel intensity summaries. These are extraction-integrity checks, not biological image-quality approval.

Further processing requires explicit user approval for each step.
