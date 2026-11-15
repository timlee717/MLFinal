# MLFinal — Rat SCG imaging mass cytometry analysis

Analysis of a September 8, 2026 imaging mass cytometry (IMC) experiment on cultured rat superior cervical ganglion cells. See [CLAUDE.md](CLAUDE.md) for the full dataset description, experimental conditions, and marker panel.

## Raw images are not in this repo

The 40 quantitative TIFFs in `01_MCD_Extraction/img/` (57 × 1000 × 1000 `float32`, ~217 MB each, ~8.5 GB total) exceed GitHub's file size limit and are excluded by `.gitignore`. To run the analysis, place a copy of those TIFFs in `01_MCD_Extraction/img/` locally. Everything else (metadata, segmentation masks, neuron assignments, panel worksheet) is tracked here.
