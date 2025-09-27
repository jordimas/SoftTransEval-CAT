# Introduction

The goal of this repository is to evaluate and develop prompts for LLMs that can be used to review English-to-Catalan translations in the software localization domain.

This work is used in real world scenarios in the context of reviewing open source translations.

This repository includes three main components:

- Evaluation dataset
- Tool to evaluate LLMs and prompts against the dataset
- Collection of winning prompts for the task

This work has been used to review the Catalan translations of the GNOME project.

# Dataset

Dataset is located at [dataset/dataset.tmx](dataset/dataset.tmx).

The dataset has the following characteristics:
- English - Catalan only
- Contains 1000 translations from the GNOME UI and documentation projects
- Includes 5% translation errors (it is imbalanced), which have been reviewed and corrected by humans

# Evaluation of different prompts

Prompts are in [config/](config/) directory.

| model | version | comment | tp | fn | fp | tn | precision | recall | f1 | time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-5 | 1 | Default prompt description | 11 | 39 | 8 | 342 | 0.58 | 0.22 | 0.32 | 1293 |
| gpt-5-mini | 1 | Default prompt description | 13 | 37 | 12 | 338 | 0.52 | 0.26 | 0.35 | 1456 |
| gemini-2.5-flash | 1 | Default prompt description | 13 | 37 | 5 | 345 | 0.72 | 0.26 | 0.38 | 840 |
| gemini-2.5-pro | 1 | Default prompt description | 15 | 35 | 9 | 341 | 0.62 | 0.3 | 0.41 | 2971 |
| gemma3 | 1 | This is the baseline | 15 | 35 | 18 | 332 | 0.45 | 0.3 | 0.36 | 1267 |
| gemma3 | 2 | Pure instructions prompt | 17 | 33 | 25 | 325 | 0.4 | 0.34 | 0.37 | 1296 |
| gemma3 | 2_1 | Pure instructions prompt v2.1 | 18 | 32 | 28 | 322 | 0.39 | 0.36 | 0.37 | 1236 |
| gemma3 | 3 | Prompt with samples | 14 | 36 | 16 | 334 | 0.47 | 0.28 | 0.35 | 1314 |
| gemma3 | 3_1 | Prompt with samples v3.1 | 8 | 42 | 6 | 344 | 0.57 | 0.16 | 0.25 | 911 |
| gemma3 | 4 | Super simple prompt | 33 | 17 | 84 | 266 | 0.28 | 0.66 | 0.4 | 3716 |
| gemma3 | 5 | Categorization prompt | 32 | 18 | 75 | 275 | 0.3 | 0.64 | 0.41 | 1776 |

Notes:
- Gemma 3 is Gemma 3 27B model
- This evalalution is done over 400 strings of which 12.50% contain errors and 87.50% are correct.

Legend:
- version: version of the prompt
- comment: comment that describes the prompt
- tp: true positive
- fp: false positive
- fn: false negative
- tn: true negative

If you are not familiar with these concepts, check the [confusion matrix](https://en.wikipedia.org/wiki/Confusion_matrix) at Wikipedia.

# Using the system to review your translation

Our current recommendation is Gemma 3 27B with prompt version 5.

If you have a file in PO format tha you want to review, follow these instructions.

1. Install the necessary dependencies:

```sh
pip install -r evaluator/requirements.txt
```

2. Download the model
```sh
make download-models
```

3. Run it in your own PO file:

```sh
python evaluator/inference.py --input FILE.po
```

The output is a FILE.txt with all the detected errors.
Expect the system to generate a large amount of false postives but the true positives are very useful.


