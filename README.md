## Overview

JPhonABX is a Japanese phonological discrimination dataset targeting moraic and accentual contrasts, proposed in [JPhonABX: Japanese Phonological Discrimination Dataset for Moraic and Accentual Minimal Pairs](TODO: paper URL) (EMNLP 2026).

This repository releases:

1. The **ABX triplet metadata** (`mora_discrimination.csv`, `accent_discrimination.csv`) that defines the dataset, plus a 500-triplet subset of each (`humaneval_mora_discrimination.csv`, `humaneval_accent_discrimination.csv`) used for the human evaluation.
2. The **evaluation code**, together with the scripts needed to prepare the referenced audio from JVS. This is the code needed to evaluate your own models on JPhonABX (see [Evaluating your own model](#evaluating-your-own-model) below).
3. The **full pipeline code** used to build the metadata from JVS audio, released for transparency and reproducibility, and so that you can modify the dataset construction if needed.

Note: JVS audio is **not** redistributed as part of this dataset, in accordance with the JVS corpus license. You will need to download it yourself.

The metadata files are in `data/`, the evaluation scripts in `evaluation/`, and the dataset construction scripts in `pipeline/`. You normally only run the two entry points at the top level, `run_evaluation.py` and `run_full_pipeline.py`.

## Dataset metadata files

`mora_discrimination.csv` and `accent_discrimination.csv` are the two main metadata files most users need. Each row describes one ABX triplet, specifying which JVS recording and time span correspond to TGT, OTH, and X, plus their speaker/gender/pitch/mora metadata.

`humaneval_mora_discrimination.csv` and `humaneval_accent_discrimination.csv` are fixed 500-triplet random subsets of the two files above, used for the human evaluation reported alongside the model evaluation. They share the same columns as their parent files.

See [DATA_FORMAT.md](DATA_FORMAT.md) for a column-by-column description of both files.

## Setup

This project was developed and tested with Python 3.12.0.

Everything below needs the JVS corpus, which is available [here](https://sites.google.com/site/shinnosuketakamichi/research-topics/jvs_corpus). Unzip it in the repository root. The zip is 3.5 GB and expands to 5.2 GB.

```bash
pip install gdown

# Replace <FILE_ID> with the Google Drive file ID listed on the page above.
gdown https://drive.google.com/uc?id=<FILE_ID>

unzip -q jvs_ver1.zip -d .
```

From here, follow [Evaluating your own model](#evaluating-your-own-model) to evaluate a model on JPhonABX, or [Building the dataset from scratch](#building-the-dataset-from-scratch) to reproduce or modify the metadata itself.

## Evaluating your own model

There are two evaluation flows, depending on whether the model hears each fragment within its utterance or on its own:

- **`with-context`** extracts features once per full JVS utterance and slices them per triplet, so the model sees each fragment in its original utterance.
- **`without-context`** extracts features per individual trimora/bimora fragment, so the model never sees the rest of the utterance.

Both need `dtw_experiment.py` and `dtw.py` from [this repository](https://github.com/JAMJU/Sel_supervised_models_perception_biases), placed in the repository root:

```bash
wget https://raw.githubusercontent.com/JAMJU/Sel_supervised_models_perception_biases/main/dtw_experiment.py
wget https://raw.githubusercontent.com/JAMJU/Sel_supervised_models_perception_biases/main/dtw.py

pip install soundfile scipy pandas transformers torch plotly pydub
```

Both also need 16 kHz copies of the JVS recordings. Creating them takes about 14 minutes and writes about 2.4 GB:

```bash
python3 run_full_pipeline.py --steps correct,resample
```

Then run either flow end to end with `run_evaluation.py`:

```bash
python3 run_evaluation.py with-context --model <model_name> --distance <distance> --layer <layer>
python3 run_evaluation.py without-context --model <model_name> --distance <distance> --layer <layer>

# e.g., python3 run_evaluation.py with-context --model imprt/kushinada-hubert-base --distance cosine --layer 0
```

`without-context` also cuts the fragments out of the 16 kHz recordings first (about 97,000 files, about 1 GB).

For a 12-layer model with 768-dimensional features, `with-context` writes about 145 GB (about 119,000 files) and `without-context` about 55 GB (about 1.17 million files); scale these by your model's hidden size. `--humaneval` brings `without-context` down to about 1.6 GB.

Each flow writes two results CSVs to `abx_results/`, one for `mora_discrimination.csv` and one for `accent_discrimination.csv`, each with one row per triplet in the same order. The accuracy can be calculated as the average of the `decision` column.

Options of `run_evaluation.py`:

- `--humaneval` scores the 500-triplet human evaluation subsets instead of the full dataset.
- `--steps score` reuses features that are already extracted, which is what you want when scoring several layers of the same model.
- `--dry-run` prints the underlying commands without running them; run those scripts directly if you need finer control.

## Building the dataset from scratch

This rebuilds `mora_discrimination.csv`, `accent_discrimination.csv`, and their human evaluation subsets from JVS audio. It is only needed to reproduce or modify the dataset construction. The full pipeline generates about 336,000 files (about 10 GB).

### Additional setup

Install the full dependency list:

```bash
pip install -r requirements.txt
```

**Corrected phoneme alignments.** These are included in the `aligned_labels_openjtalk` folder of the `jvs_hiho` repository.

```bash
wget https://github.com/Hiroshiba/jvs_hiho/archive/refs/heads/master.zip

unzip -q master.zip 'jvs_hiho-master/aligned_labels_openjtalk/*'
```

**Helper scripts.** Download `surface2katakana_with_acc.py` and `parse_accent.py` from [this repository](https://huggingface.co/spaces/AkitoP/whisper-japanese-phone-demo/tree/main).

```bash
wget https://huggingface.co/spaces/AkitoP/whisper-japanese-phone-demo/resolve/main/surface2katakana_with_acc.py
wget https://huggingface.co/spaces/AkitoP/whisper-japanese-phone-demo/resolve/main/parse_accent.py
```

In `parse_accent.py`, make the following changes:

1. Replace line 3 with `s = [x for x in s if x not in ['^', '#', '$']]`.
2. Replace line 9 with `chars = s`.
3. Comment out line 34 (`marks.append(current_mark)`).

### Running the pipeline

Use the pipeline runner to build the complete dataset, including the human evaluation subsets:

```bash
python3 run_full_pipeline.py
```

The runner executes the following stages in order:

- `correct` : `pipeline/correct_mistake.sh` (less than 1 min)
- `resample` : `pipeline/convert_to_16kHz.py` (13 min)
- `align` : `pipeline/align_morae.py` (2 min)
- `mora_seq` : `pipeline/make_mora_seq_csv.py` (less than 1 min)
- `pairs` : `pipeline/make_abx_pairs.py` (less than 1 min)
- `pitch` : `pipeline/annotate_pitch.py` (6.5 h, on a GPU)
- `f0` : `pipeline/annotate_f0.py` (18.5 h)
- `extract` : `pipeline/extract_all_trimora_bimora.py` (14 min)
- `abx_dataset` : `pipeline/make_abx_dataset.py` (4 min)
- `final` : `pipeline/make_final_datasets.py` (9 min)
- `human_eval` : `pipeline/human_evaluation.py` (less than 1 min)

Unless otherwise specified, each step was run on a CPU.

One further stage, `triplet_folder` (`pipeline/create_triplet_folder.py`), is available but not run by default. It copies the human evaluation subsets' fragments into `humaneval/`, arranged as they were presented to the listeners, with the A/B order randomized, and is only needed to reproduce the listening test itself.

Use `--steps` to run only selected stages. For example:

```bash
python3 run_full_pipeline.py --steps align,mora_seq,pairs
```

Use `--dry-run` to preview the correction and resampling steps before making any changes:

```bash
python3 run_full_pipeline.py --dry-run
```

## License

The code in this repository is licensed under MIT. Both evaluating a model and building the dataset rely on third-party resources that are not part of this repository and keep their own license/usage terms:

- the JVS corpus (evaluation and building),
- `dtw_experiment.py` and `dtw.py` (evaluation; `dtw.py` states GPL-3.0),
- the jvs_hiho alignment data and the Hugging Face Space helper scripts (building the dataset).

**Users must obtain and use these third-party resources in compliance with their respective licenses, independently of this repository's license.**

## Citation

If you use JPhonABX, please cite:

```bibtex
TODO: BibTeX entry
```
