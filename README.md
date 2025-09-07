# Introduction

The goal of this repository is to evaluate and develop prompts for LLMs that can be used to review English-to-Catalan translations in the software localization domain.

This work is used in real world scenarios in the context of reviewing open source translations.

This repository includes three main components:

- Evaluation dataset
- Tool to evaluate LLMs and prompts against the dataset
- Collection of winning prompts for the task

# Dataset

Dataset is at [dataset/dataset.tmx](dataset/dataset.tmx) file.

The dataset has the following characteristics:
- English - Catalan only
- Contains 1,000 translations from the GNOME UI and documentation projects
- Includes 10% translation errors (it is imbalanced), which have been review and corrected by humans

# Evaluation of differents prompts

Prompts are in [config/](config/) directory.

| model | version | comment | tp | fp | fn | tn | precision | recall | f1 | time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gemma3 | 1 | This is the baseline | 11 | 14 | 9 | 166 | 0.44 | 0.55 | 0.49 | 1702.62 |
| gemma3 | 2 | Pure instructions prompt | 10 | 7 | 10 | 173 | 0.59 | 0.5 | 0.54 | 1588.4 |
| gemma3 | 2_1 | Pure instructions prompt v2.1 | 10 | 5 | 10 | 175 | 0.67 | 0.5 | 0.57 | 1432.67 |
| gemma3 | 2_2 | Pure instructions prompt v2.2 | 3 | 3 | 17 | 177 | 0.5 | 0.15 | 0.23 | 1120.46 |
| gemma3 | 3 | Prompt with samples | 6 | 2 | 14 | 178 | 0.75 | 0.3 | 0.43 | 1307.63 |
| gemma3 | 3_1 | Prompt with samples v3.1 | 4 | 4 | 16 | 176 | 0.5 | 0.2 | 0.29 | 1217.62 |
| gemma3 | 3_2 | Prompt with samples v2.2 | 8 | 85 | 12 | 95 | 0.09 | 0.4 | 0.14 | 1701.67 |
| gemma3 | 4 | Super simple prompt | 15 | 36 | 5 | 144 | 0.29 | 0.75 | 0.42 | 7969.02 |
| gemma3 | 5 | Categorization prompt | 16 | 51 | 4 | 129 | 0.24 | 0.8 | 0.37 | 6007.84 |

Legend:
- version: version of the prompt
- comment: comment that describes the prompt
- tp: true positive
- fp: false positive
- fn: false negative
- tn: true positive
