# Rat SCG imaging mass cytometry handoff

> **Repo layout (MLFinal, option 2):** this repo was reorganized for the NGF-vs-BDNF project. The paths below come from the original lab handoff. In this repo they live at:
> `01_MCD_Extraction/img/` → `Data/raw/images/` (local only, gitignored) ·
> `01_MCD_Extraction/metadata/{fov_annotation,panel}.csv` → `Data/raw/metadata/` ·
> `04_DeepCell_Segmentation/manifest.csv` → `Data/raw/metadata/manifest.csv` ·
> `04_DeepCell_Segmentation/masks/` → `Data/raw/masks/` ·
> `06_Neuron_ID/{cell_neuron_assignments,condition_thresholds}.csv` → `Data/raw/neuron_labels/`.
> Files not used for option 2 (`images.csv`, `acquired_channels.csv`, `settings.json`, `thresholds_used/`, the staining `.xlsx`, extraction logs) were removed from the repo; they remain in git history.

This is an exploratory analysis of a September 8, 2026 imaging mass cytometry (IMC) experiment on mass cultures of wild-type rat superior cervical ganglion (SCG) cells. The cultures contain sympathetic neurons and other cells. The goal is to use the quantitative images and existing masks to build your own analysis of how signaling varies with trophic-factor deprivation, KCl, and acute NGF or BDNF exposure.

## Experiment and comparisons

1. **Culture.** Before deprivation, neurons were cultured for four days in DMEM with FBS and 50 ng/mL nerve growth factor (NGF).
2. **Deprivation.** For 12 hours, deprivation groups received DMEM without FBS or added NGF, with an NGF-neutralizing antibody. The experiment notes record 1 µg/mL anti-NGF and 12.5 mM KCl where indicated.
3. **Wash and treatment.** Before acute stimulation, the treatment groups were washed with DMEM containing no FBS, NGF, or anti-NGF. The notes record two 5-minute washes and complete medium replacement. The acute groups received fresh KCl-containing treatment medium without anti-NGF, with either 100 ng/mL NGF or 200 ng/mL brain-derived neurotrophic factor (BDNF) for 30 minutes before fixation. The nLwK group received a mock wash and kept its original deprivation medium.

| Code | Condition |
|---|---|
| `CoN` | Continuous NGF, 50 ng/mL. |
| `nLnK` | 12-hour deprivation without added KCl. |
| `nLwK` | 12-hour deprivation with 12.5 mM KCl. |
| `N` / 30min NGF | 12-hour deprivation with KCl, then 100 ng/mL NGF for 30 minutes. |
| `B` / 30min BDNF | 12-hour deprivation with KCl, then 200 ng/mL BDNF for 30 minutes. |

Use these comparisons for treatment interpretation:

| Question | Comparisons |
|---|---|
| Deprivation and the KCl condition | CoN vs nLnK, CoN vs nLwK, nLnK vs nLwK |
| Acute NGF | N vs nLwK, N vs CoN |
| Acute BDNF | B vs nLwK, B vs CoN |

nLwK is the matched deprivation reference for the acute treatments. The acute comparisons include fresh treatment medium as well as ligand exposure. The exact nLwK fixation time relative to the 30-minute treatment window is unconfirmed. FBS percentage, added KCl in CoN and the wash solution, rat strain and age, and the mapping from animals or culture preparations to wells are also unconfirmed in the handoff records.

There are two wells per treatment, five ROIs per treatment in Well 1 and three in Well 2, totaling 40 ROIs. The recorded laser settings are 1 for Well 1 and 2 for Well 2. The corresponding MCD `AblationPower` values are 0 and 1. Well and laser setting are confounded. Start with within-well comparisons and use the other well as a separate check. Keep the cell → ROI → well hierarchy when reporting effects. The ROI counts describe subsampling, and the biological replicate structure needs the culture-preparation records.

## Analysis inputs

Use the following paths relative to the dataset root. Their current source root is `/Users/yangcheng/Desktop/IMC_Rat_SCG_Culture_09082026`.

| Path | Contents |
|---|---|
| `01_MCD_Extraction/img/` | 40 quantitative TIFFs, one per ROI, totaling about 9.12 GB. Each stack is 57 × 1,000 × 1,000 in channel × Y × X order, `float32`, at 1 µm per pixel in X and Y. |
| `01_MCD_Extraction/metadata/fov_annotation.csv` | ROI ID (`fov`), treatment, well, ROI number, laser setting, MCD acquisition and exported image filename (`image`). |
| `01_MCD_Extraction/metadata/panel.csv` | The 57 intensity planes in TIFF order. Use zero-based row position after the header for Python indexing. The `ilastik` column is one-based. |
| `01_MCD_Extraction/metadata/images.csv` and `01_MCD_Extraction/metadata/acquired_channels.csv` | Steinbock image metadata and the original acquisition schema. The acquisition schema also lists coordinate fields. |
| `04_DeepCell_Segmentation/masks/` | 40 original all-cell label TIFFs, about 2.2 MB total. Each is 1,000 × 1,000 in Y × X order, `uint32`. Zero is background. Positive integers are separate regions and may have gaps. |
| `04_DeepCell_Segmentation/manifest.csv` and `04_DeepCell_Segmentation/settings.json` | ROI key (`roi`), relative mask filename, exact source TIFF filename, region counts, and the segmentation configuration. |
| `IMC_Rat_09082026_panel/Cheng_IMC__Ab_Staining_09082026.xlsx` | Staining worksheet. Use `panel.csv` as the source of truth for which planes were acquired and their order. |
| `06_Neuron_ID/cell_neuron_assignments.csv` | Optional Well 1 assignments covering both gate-passing and ungated labels, with recorded marker means and gate settings. |
| `06_Neuron_ID/condition_thresholds.csv` and `06_Neuron_ID/thresholds_used/` | Optional reference for the saved neuron gates. |

**Join by ROI.** Match `fov_annotation.csv:fov` to `manifest.csv:roi`, check that `image` equals `source_image`, and use the filenames in the two tables. For example, `CoN_1_01` maps to `01_MCD_Extraction/img/CoN_1_01_001.tiff` and `04_DeepCell_Segmentation/masks/CoN_1_01_nuclear_as_WC_mask.tif`. Identify a region by `(ROI, mask_label)`, such as `CoN_1_01:42`. Label numbers are local to each ROI. Retain the IDs when deriving new measurements so you can trace cells back to their source images.

**Preprocessing already applied.** Steinbock 0.16.3 extracted the MCD acquisitions with its hot-pixel filter set to HPF = 50. The TIFFs precede the project’s later marker-specific artifact review and cell exclusions. Extraction applied no spillover correction or intensity normalization. Use the Step 01 TIFFs for measurements. Step 03 Fiji images are contrast-scaled 8-bit previews for visual inspection.

**Mask semantics.** DeepCell Mesmer used Ir191/Ir193 nuclear inputs and TH/p75NTR/Ret cytoplasmic inputs. The saved labels are the unexpanded nuclear instance output with a strict area cutoff of >50 µm². This export is the starting set of all segmented regions. Ir191 and Ir193 are redundant readouts of the same DNA intercalator. They are nuclear stains whose signal often extends across the cell body in these IMC images. The project used these regions directly for cell-level measurements. Inspect representative Ir and TH overlays before interpreting mask area as soma size or a marker mean as whole-cell abundance.

## Marker panel

The quantitative TIFFs retain 17 antibody channels, the two iridium channels, and 38 additional acquisition channels. The placement of each plane is recorded in `panel.csv`.

| Role | Marker | Isotope | Use note |
|---|---|---|---|
| Neuronal context | Tuj1 | 89Y | Neuronal processes and morphology. |
| Neuronal context | TH | 163Dy | Sympathetic-neuron marker used in the saved gate. |
| Receptor | TrkA | 165Ho | Measured for phenotyping and gate review. |
| Receptor | p75NTR | 161Dy | Used in the saved neuron gate. |
| Receptor | Ret | 171Yb | Used in the saved neuron gate. |
| Signaling | p-Tyr | 146Nd | Broad phosphotyrosine readout. |
| Signaling | p-Akt (S473) | 142Nd | S473 phosphosite. |
| Signaling | p-Akt (T308) | 169Tm | T308 phosphosite. |
| Signaling | p-PLCγ2 | 144Nd | |
| Signaling | p-S6 | 149Sm | |
| Signaling | p-CREB | 176Yb | |
| Signaling | p-NFκB | 166Er | |
| Signaling | p-ATM | 159Tb | |
| Signaling | p-c-Jun | 162Dy | **Unreliable in this experiment. Preserve the plane and metadata. Exclude from biological interpretation.** |
| Cell state | c-Fos | 155Gd | |
| Cell state | H3K9ac | 115In | |
| Cell state | Cleaved caspase-3 | 173Yb | **Unreliable in this experiment. Preserve the plane and metadata. Exclude from biological interpretation.** |
| DNA intercalator | Ir191 | 191Ir | Redundant with Ir193. |
| DNA intercalator | Ir193 | 193Ir | Redundant with Ir191. |

## Working with the dataset

The IMC workflow used here starts with MCD extraction, channel and image QC, and DeepCell segmentation. From the shared starting point, load the quantitative images and masks, inspect image and mask alignment, quantify marker intensity per region, assign or explore cell populations, and summarize treatment responses while retaining ROI and well identifiers. Pixie pixel clustering and marker-specific artifact inspection are available for exploratory QC.

Neuronal phenotyping considered **TH, TrkA, p75NTR, and Ret**, with Tuj1 as additional context. In the saved assignment script, the decision rule is that TH, p75NTR, and Ret must all pass condition-specific cutoffs. The script measures TrkA and Tuj1 for reference. A cell outside the saved gate is **ungated** and may include a dim or missed neuron. One project is to cluster the ungated population, inspect cluster marker profiles and image overlays, and ask whether any candidate non-neuronal populations show treatment-associated signaling. Use marker evidence before assigning cell-type names.

## Questions to explore

### Can you define a meaningful signaling baseline?

Use nLwK as the starting reference for CoN, 30-minute NGF, and 30-minute BDNF. The working assumption is that after 12 hours of deprivation with KCl, most nLwK neurons have basal activity for most signaling markers. One simple rule defines the central nLwK range by the 5th and 95th percentiles separately for each marker, then applies those fixed cutoffs across the groups. Compare each fraction strictly below or above the corresponding cutoff. Ties can change the observed tail fractions, especially for zero-valued signals.

The percentile rule defines what is typical under nLwK by construction. The central 90% assumption is a starting hypothesis, and KCl can influence signaling. Can you find a reproducible boundary for any marker across nLwK ROIs? Try checking for a stable separation in the distribution and holding out whole ROIs when assessing it. For a graded distribution, compare full distributions and show how conclusions depend on the cutoff. A threshold labeled biologically basal would benefit from independent low-activity or stimulated controls. [Depolarization and neurotrophin signaling in sympathetic neurons](https://pmc.ncbi.nlm.nih.gov/articles/PMC2169479/) · [Density-based gating example](https://doi.org/10.1093/bioinformatics/btu677)

### Which marker pairs are co-high or co-low in the same cells?

Within an ROI, ask whether two markers are co-high or co-low more often than expected from each marker’s individual frequency. Use cells with usable measurements for both markers to calculate the two individual fractions and the joint fraction. Under independence the expected joint fraction is the product of the individual fractions. Check whether any excess recurs across ROIs in the same treatment, and compare it across the planned contrasts.

### Which markers respond in coordination across treatments?

For each planned treatment contrast, estimate each marker’s shift in intensity or responder fraction. Look for markers that consistently move together, move in opposite directions, or coordinate only under one condition. For example, two markers may rise after NGF while only one shifts after BDNF. Check whether the pattern recurs across ROIs. This question concerns how **treatment response profiles** move together. The co-high/co-low question concerns which **individual cells** share a response.

### Can a pathway model explain or predict the response?

Choose a small set of markers and propose activating or inhibitory links. Use Claude to help find primary studies, then check the papers for the cell type, stimulus, phosphosite, and whether the evidence supports a direct or indirect link. Identify which links are assumptions. Write down predictions and what would make you revise the model. If you fit a prediction model, test it on held-out whole ROIs. A model may fit these endpoint data through multiple mechanisms. A time course or targeted perturbation can help test directionality. [Perturbation-based signaling network study](https://pubmed.ncbi.nlm.nih.gov/15845847/)

## Script reference

These scripts are optional resources for independent analysis. The catalog describes what the code does. Local paths below refer to the source copies on Cheng’s computer:

- **Desktop project:** `/Users/yangcheng/Desktop/IMC_Rat_SCG_Culture_09082026`
- **Codex checkout:** `/Users/yangcheng/Documents/ChatGPT/IMC_Rat_SCG_09082026`
- **Earlier IMC prototypes:** `/Users/yangcheng/Desktop/IMC_Prototype_scripts`

Use the filesystem paths in a shared copy of the dataset. Several historical scripts hard-code Cheng’s Desktop path, local Conda Python, or an output folder. Read the source or its nearby README, adjust the paths in a working copy, and use a separate output directory for a trial run. Desktop analysis notebooks generally used `ark_env_clean` (Python 3.10). The tutorial contains a `requirements.txt` for its Python preparation code. Node.js is used for its `.cjs` tools and tests, Fiji for `.ijm` macros, and Jupyter for `.ipynb` notebooks. Files with the same name in different folders can have different defaults.

For a starting example of ROI-to-mask measurement, read `06_Neuron_ID/measure_marker_means.py` in the Desktop project. For a reusable TIFF and metadata loader, start with `All_Marker_Tutorial/code/prepare_dataset.py` in the Codex checkout and follow the tutorial README for the input format. For exploratory clustering of ungated cells, the earlier `3_Pixie_Cluster_Cells_new_v3.py` and `7_Clustering_based_on_Signaling_Markers.py` show two approaches that can be adapted.

### Desktop project, Steps 01–11

| Directory | Files and purpose |
|---|---|
| `01_MCD_Extraction/logs/` | `prepare_mcd_extraction.py` inventories MCD files and prepares extraction metadata. `run_mcd_extraction.py` runs Steinbock and collates the TIFFs and validation outputs. Useful for extraction provenance. |
| `03_FIJI_based_manual_BC/logs/` | `manual_BC.ijm` and `revised_BC.ijm` generate initial and revised contrast-scaled 8-bit inspection images. |
| `04_DeepCell_Segmentation/` | Saved masks, manifest, and settings. The original computation is in `IMC_09082026/DeepCell_IMC_09082026.ipynb` on UVA HPC, as recorded in the segmentation chat. A local copy of the notebook was not found. The local `Nuclear_Masks_as_WC.tar.gz` archive in Downloads contains the masks and export metadata. |
| `05_Neuron_ID_Marker_Gating/` | `select_rois.py` selects a pilot ROI per condition. `measure_marker_means.py` measures neuronal markers on saved labels. `transform_arcsinh.py` computes transformed means. `prepare_roi_viewer_assets.py` builds ROI and mask previews. `plot_marker_distributions.py` builds interactive distributions for gate review. `05_Neuron_ID_Marker_Gating.ipynb` is the notebook entry point. `plot_marker_distributions_before_thresholds.py` and `plot_marker_distributions_before_viewer.py` preserve earlier plot versions. `archive_three_marker_version/05_Neuron_ID.ipynb` and its three Python helpers preserve the earlier gate-review workflow. |
| `06_Neuron_ID/` | `measure_marker_means.py` measures the five phenotyping markers across Well 1. `apply_neuron_thresholds.py` applies the saved gates and writes assignment tables and neuron-only masks. `create_neuron_qc.py` generates TH overlays. `06_Neuron_ID.ipynb` documents and can rerun the step. |
| `07_Neuron_Pseudobulk_Heatmap/` | `build_pseudobulk_heatmap.py` computes mask-level marker means and pooled condition fold changes. `07_Neuron_Pseudobulk_Heatmap.ipynb` wraps and displays that workflow. |
| `08_Abnormality_Inspection/` | `build_abnormality_inspection.py` creates per-marker ROI montages and adds outlines for gate-passing neurons. |
| `09_Neuron_Marker_Violin_Plots/` | `build_marker_violins.py` makes cell-level marker violin plots with ROI-colored points. `09_Neuron_Marker_Violin_Plots.ipynb` documents and can rerun the plotting. |
| `10_Outlier_Cell_Inspection/p_Akt_S473/` | `build_outlier_review.py` finds high-intensity p-Akt candidates and creates corresponding multi-channel cell crops and a viewer. |
| `11_Pixie_Neurite_Masks/` and `11_Pixie_Neurite_Masks_Version_A/` | `step11_pixie.py` prepares pixel data, fits and applies Pixie clustering, and exports reviewed masks. `step11_ui.py` builds the review UI. `11_Pixie_Neurite_Masks.ipynb` drives the steps. `Launch_Step11.command` opens the notebook environment. `test_step11.py` checks core behavior. `verify_notebook.py` checks the notebook. `display_repair_backup/` contains an earlier UI implementation. |
| `11_Pixie_Neurite_Masks_Version_B/` | `11B_Pixie_Neurite_Masks.ipynb` and `Launch_Step11B.command` are the notebook and launcher. `step11_features.py` builds intensity and reference features. `step11_pixie.py` fits, applies, and exports pixel clusters. `step11_diagnostics.py` compares and visualizes pixel runs. `step11_ui.py` provides spatial review. `jupyter_server_config.py` configures the local server. `test_step11.py`, `test_step11_features.py`, `test_step11_diagnostics.py`, and `test_step11_ui_b.py` cover those components. |

### Desktop project, Steps 12–14

Step 12 paths below are relative to `12_Hot_Pixel_Removal_and_Noise_Correction/`. Its `Annotation_Exports/` directory contains the cutoff and review records consumed by the quantification scripts.

| Directory | Files and purpose |
|---|---|
| `All_Marker_pipeline/01_Neuronal_Review/` | `Open_neuronal_review.command` and `scripts/serve_neuronal_review.py` launch the viewer. `scripts/build_interface.py` builds it, `scripts/preview_images.py` builds image previews, `prototype/neuron_review.js` supplies review interactions, and `scripts/all_marker_export.js` exports annotations. `inputs/*.js` are generated per-marker data, and `neuronal_review/*/assets/neuron_review.js` are per-marker viewer copies. |
| `All_Marker_pipeline/02_Hot_Pixel_Aggregate_Inspection/` | `scripts/build_data.py` catalogs raw pixels, components and cell geometry. `scripts/cutoff_engine.py` computes cutoff-dependent components and cell rules. `scripts/cutoff_interface.py` connects the engine to the viewer. `scripts/build_interface.py` assembles the inspector, and `prototype/aggregate_viewer.js` supplies interactions. `scripts/verify_data.py` verifies components and geometry. `Open_aggregate_inspector.command` and `scripts/serve_inspector.py` launch and serve it. `markers/*/assets/` holds each generated viewer and manifest. |
| `All_Marker_pipeline/03_Noise_Spread/` | `scripts/build_data.py` prepares candidate aggregate crops, and `scripts/build_interface.py` assembles the app. `endpoint.js` estimates spread endpoints from image profiles. `viewer.js`, `bootstrap.js`, and `catalog.js` connect the views to the crop catalog. `scripts/core_outline.js`, `manual_spread.js`, and `review_controls.js` handle outlines, manual masks, and review/export controls. `Open_noise_spread.command` and `scripts/serve.py` launch it. `scripts/test_bright_rule.cjs`, `test_manual.cjs`, `test_masks.cjs`, and `test_render.cjs` check the bright-pixel logic, edits, mask calculations, and rendering. `prototype/` holds the earlier `endpoint.js`, `viewer.js`, and `test_endpoints.cjs`. |
| `scripts/` | `build_final_violins.py` uses source TIFFs, original masks, saved neuron assignments, and reviewed artifact inputs to compute per-marker exclusion and retained-pixel intensity tables and plots. `step09_style_reference.py` provides plot style. `validate_final.py` checks rules, intensity calculations, and saved tables. This historical code uses its saved marker set. Apply the two current reliability flags when adapting it. |

The p-Akt prototypes are under `12_Hot_Pixel_Removal_and_Noise_Correction/p_Akt_S473/`. They provide examples of different QC approaches.

| Subdirectory | Files and purpose |
|---|---|
| `scripts/` | `01_background_violin.py` and `02_biological_structure_violin.py` plot background and biological-region pixel distributions. `03_background_tail.py` computes intensity exceedance curves. `04_05_background_threshold_images.py` visualizes candidate thresholds and crops. `create_original_overlays.py` overlays source masks and images. `inspect_background_tail.py` inspects high background values, and `summarize_neuron_pAkt.py` summarizes per-neuron measurements. `archive/01_intensity_ranges.py` and `archive/02_background_overlay.py` are earlier range and overlay figures. |
| `scripts/second_attempt/` | `01_compartment_distributions.py` describes pixels by compartment. `02_neuron_pixel_contribution.py` quantifies the contribution of bright pixels to region means. `03_build_neuron_review.py`, `03_serve_neuron_review.py`, `03_test_neuron_review.cjs`, and `neuron_review.js` build, serve, and check the viewer. `04_apply_mask_review_exclusions.py` applies prototype annotations. `05_01_pAkt_before_after.py` creates comparisons and `05_02_processed_pAkt_violin.py` plots processed intensity. `apply_pAkt_gt5_well1.py` applies the prototype cutoff. `correct_pAkt_background_well1.py` implements a separate prototype background subtraction. |
| `scripts/hot_pixel_aggregates/` and `hot_pixel_aggregates/` | `build_aggregate_viewer.py`, `aggregate_viewer.js`, `serve_aggregate_viewer.py`, and `verify_aggregate_geometry.py` build, display, serve, and verify the p-Akt aggregate review. `Open_aggregate_viewer.command` starts the built viewer with its generated `assets/manifest.js`. |
| `scripts/laser_refraction/` and `laser_refraction/` | `data_pipeline.py` and `build_ring_viewer.py` prepare aggregate crops and ring profiles. `endpoint.js` computes candidate spread and `viewer.js` displays reviews. `serve_ring_viewer.py` and `Open_ring_profiles.command` launch the app with generated `catalog.js`, `data.js`, and `defaults.js`. `check_viewer.cjs`, `test_endpoints.cjs`, and `verify_all25.py`, `verify_batch_export.py`, `verify_endpoints.py`, `verify_profiles.py` check its behavior and data. Older detector and viewer variants live in `backups/`. |
| `figures_2nd_attempt/03_neuron_review/` and `figures_3_3rd_attempt_after_correction_and_exclusion/` | The second-attempt folder contains `Open neuron reviewer.command` and the generated viewer with `assets/review_data.js` as its input. The third-attempt `apply_rules_and_plot.py` runs an earlier exclusion-and-plotting workflow. `nLnK_outlier_review/inspect_nlnk.py` and `resize_review.py` make and resize focused review panels. |

| Directory | Files and purpose |
|---|---|
| `13_Violin_Plot_Cell_Inspection/` | `viewer.js` provides interactive violin and cell-crop inspection. `Open_violin_plot_cell_inspection.command`, `scripts/launch.py`, and `scripts/server.py` launch and serve the app. `scripts/install_package.py` assembles the local viewer, `scripts/add_ir193_panel.py` adds the Ir193 crop panel, and `scripts/check_test_api.py` and `scripts/validate.py` check the API and generated package. |
| `14_Further_Analysis/01_Fold_Change_Heatmaps/` | `build_fold_change_heatmaps.py` summarizes relative marker intensity by condition. |
| `14_Further_Analysis/02_95pct threshold cutoff/` | `build_threshold_bargraphs.py` computes upper nLwK cutoffs and plots fractions above them. |
| `14_Further_Analysis/03_neuron_above_threshold_FC/` | `build_threshold_fc_heatmap.py` plots fold changes in above-cutoff fractions. |
| `14_Further_Analysis/04_High_n_Low_Cuttoff/` | `build_high_low_cutoffs.py` computes lower and upper nLwK cutoffs. |
| `14_Further_Analysis/05_High_n_Low_fraction_FC/` | `build_high_low_fraction_heatmaps.py` summarizes above- and below-cutoff fractions. |
| `14_Further_Analysis/06_Marker_Pair_High_Low_FC/` | `build_marker_pair_heatmaps.py` summarizes both-high and both-low cell fractions for marker pairs. `re-fined_Marker_Pair_FC/build_refined_pair_heatmaps.py` builds the selected-pair version. |
| `rerun_history/20260927_threshold_refresh/` | `preserve_and_prepare.py` snapshots inputs and prepares a threshold refresh. `before/` preserves older scripts and data for reproducibility. |

### Codex checkout and portable tutorial

| Directory | Files and purpose |
|---|---|
| Checkout root | `prepare_mcd_extraction.py` and `run_mcd_extraction.py` are extraction-script copies. `create_single_channel_visualizations.py` exports channel inspection images. `prepare_step04.py`, `update_step03_ranges.py`, and `validate_step04.py` configure and verify Fiji display scaling. The `step04` names in this group reflect older numbering for the Fiji stage. |
| `All_Marker_Tutorial/` | `Guided_Inspection.ipynb`, `serve.py`, and `Open_tutorial.command` guide and launch the tutorial. `requirements.txt` lists the Python dependencies for data preparation. `publication/IMC-Hot-Pixel-Inspection-and-Noise-Exclusion/` in the checkout contains the release copy. |
| `All_Marker_Tutorial/code/` | `prepare_dataset.py` validates TIFF, mask, and metadata inputs, measures per-label marker intensity, and prepares portable review files. `quantify_marker.cjs` computes marker-specific quantification from prepared data and review inputs. `build_example.py` packages teaching inputs. `build_teaching_figures.py`, `build_spread_figures.py`, and `plot_quantification_example.py` render examples. `validate_example.py`, `verify_frozen_spread.cjs`, `check_browser.cjs`, and `check_portable_gallery.cjs` verify the bundle and viewers. `test_preparation.py`, `test_aggregate_engine.cjs`, `test_quantify_marker.cjs`, `test_review_contracts.cjs`, `test_spread_engine.cjs`, and `test_spread_worker.cjs` cover those components. |
| `All_Marker_Tutorial/interface/` | `review.js`, `aggregates.js`, and `spread.js` are the cell, aggregate, and spread viewers. `aggregate_engine.js` and `spread_engine.js` implement their calculations, with `aggregate_worker.js` and `spread_worker.js` running work in the browser background. `example/review/` contains the deployed viewer copies for the teaching example. |
| `outputs/pAkt_S473_reconstruction/scripts/` | `prepare_frozen_inputs.py` prepares the saved teaching reconstruction inputs. `check_spread_engine.cjs` and `validate_reconstruction.py` verify it. `propose_missing_reference.cjs` and `plot_provisional_reference.py` generate and display a draft review reference. |
| `outputs/step12_pAkt_diagnostics/`, `outputs/step12_pAkt_structure_review/`, `outputs/step12_figure01/`, `outputs/step12_figure02/`, `outputs/refraction_explanation/`, and `outputs/step11b_presentation_overlays/` | `step12_diagnostics.py` computes pixel and cell summaries and `test_step12.py` checks them. The `create_figures.py`, `create_figure01.py`, `create_figure02.py`, `illustrate_detector.py`, and `create_two_panel_figures.py` scripts render study-specific diagnostic, method, or overlay figures. |
| `outputs/step12_laser_refraction/` and `outputs/step12_refraction_rings/` | In `scripts/laser_refraction/`, the early detector’s `build_viewer.py`, `detector.py`, `serve_viewer.py`, `verify_detector.py`, and `viewer.js` build, compute, serve and check candidate spread. `laser_refraction/Open_laser_refraction.command` launches that prototype. The ring-profile folder mirrors the ring viewer and checks listed above and adds `install_viewer.py` to install its generated viewer. |
| Other mirrored analysis folders | The Codex checkout’s `11_Pixie_Neurite_Masks*/` and `outputs/All_Marker_pipeline/`, `outputs/step12_violin/`, `outputs/step12_hot_pixel_aggregates/`, `outputs/step12_second_attempt/`, `outputs/step12_final_violins/`, `outputs/step12_third_attempt/`, `outputs/step14_*/`, and `outputs/threshold_rerun_20260927/` contain working copies or historical versions of the corresponding scripts above. |
| `.ir_build/`, `.ppt_build/`, `.step3_revision/`, `.step4_ppt/` | Presentation helpers. `export_ir.py` and `append_ir.mjs` add iridium panels. `prepare.py` and `preserve*.py` prepare or snapshot inputs. `build.mjs`, `inspect.mjs`, `render*.mjs`, `finalize*.mjs`, `repair.py`, and `validate_images.py` build, inspect, render, finalize, repair, or verify slide images. |

### Earlier IMC prototypes

These optional scripts are from earlier SCG IMC work. Review their dataset assumptions and channel mappings before reuse.

| Files | Purpose |
|---|---|
| `1_Segment_Image_Data.py` | Prepares input images for Mesmer and extracts cell features from segmentation. |
| `2_Pixie_Cluster_Pixels_new_v2.py`, `3_Pixie_Cluster_Cells_new_v3.py` | Fit pixel- and cell-level clustering workflows and their inspection outputs. |
| `4_Post_Clustering_Tasks_new_v4.py`, `5_Signaling_Responses.py` | Summarize marker signaling and compare groups after selecting cell types. |
| `6_per_cell_signlaing_response_and_coresponder.py` | Calculates individual cell responses and joint responder patterns. |
| `7_Clustering_based_on_Signaling_Markers.py`, `8_Overlay_Clusters.py` | Cluster by signaling profiles and map cluster labels back onto images. |
| `9_pS6_clCasp3_spillover_diagnostic.py`, `9_pS6_clCasp3_spillover_diagnostic_clean_restart.py`, `9_spillover_pS6_CC3.py` | Earlier adjacent-channel interference diagnostics. They use an earlier panel layout. |
| `10_test_per_marker_responder_FC.py` | Explores marker-specific responder fractions and fold changes. |

Generated per-marker assets, notebook checkpoints, dated backups, and repeated release copies share the purposes of their source code above.
