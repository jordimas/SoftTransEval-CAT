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
| gpt-5 | 1 | Default prompt description | 10 | 41 | 5 | 944 | 0.67 | 0.2 | 0.3 | 4665 |
| gpt-5-mini | 1 | Default prompt description | 14 | 37 | 29 | 920 | 0.33 | 0.27 | 0.3 | 5200 |
| gemini-2.5-flash | 1 | Default prompt description | 13 | 38 | 16 | 933 | 0.45 | 0.25 | 0.33 | 3032 |
| gemini-2.5-pro | 1 | Default prompt description | 15 | 36 | 19 | 930 | 0.44 | 0.29 | 0.35 | 7257 |
| gemma3 | 1 | This is the baseline | 16 | 35 | 33 | 916 | 0.33 | 0.31 | 0.32 | 3476 |
| gemma3 | 2 | Pure instructions prompt | 18 | 33 | 50 | 899 | 0.26 | 0.35 | 0.3 | 3732 |
| gemma3 | 2_1 | Pure instructions prompt v2.1 | 19 | 32 | 56 | 893 | 0.25 | 0.37 | 0.3 | 3701 |
| gemma3 | 3 | Prompt with samples | 14 | 37 | 41 | 908 | 0.25 | 0.27 | 0.26 | 4156 |
| gemma3 | 3_1 | Prompt with samples v3.1 | 8 | 43 | 12 | 937 | 0.4 | 0.16 | 0.23 | 3100 |
| gemma3 | 4 | Super simple prompt | 34 | 17 | 210 | 739 | 0.14 | 0.67 | 0.23 | 8995 |
| gemma3 | 5 | Categorization prompt | 33 | 18 | 214 | 735 | 0.13 | 0.65 | 0.22 | 5974 |

Notes:
- Gemma 3 is Gemma 3 27B model quantified at 8 bits
- This evaluation is done over 400 strings of which 12.50% contain errors and 87.50% are correct.

Legend:
- version: version of the prompt
- comment: comment that describes the prompt
- tp: true positive
- fp: false positive
- fn: false negative
- tn: true negative

If you are not familiar with these concepts, check the [confusion matrix](https://en.wikipedia.org/wiki/Confusion_matrix) at Wikipedia.

# Using the system to review your translation

Our current recommendation is Gemma 3 27B with prompt version 1.

If you have a file in PO format that you want to review, follow these instructions.

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
Expect the system to generate a large amount of false positives but the true positives are very useful.


