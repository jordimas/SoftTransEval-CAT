# Introduction

The goal of this repository is to evaluate and develop prompts for LLMs that can be used to review English-to-Catalan translations in the software localization domain.

This work is used in real world scenarios in the context of reviewing open source translations.

This repository includes three main components:

- Evaluation dataset
- Tool to evaluate LLMs and prompts against the dataset
- Collection of winning prompts for the task

# Dataset

The dataset has the following characteristics:
- English - Catalan only
- Contains 1,000 translations from the GNOME UI and documentation projects
- Includes 10% translation errors (it is imbalanced), which have been review and corrected by humans

# Evaluation of differents prompt

| date_time | model | Version | Comment | tp | fp | fn | tn | precision | recall | f1 | total_time | strings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-09-06 17:54:56 | gemma3 | 1 | This is the baseline | 11 | 14 | 9 | 166 | 0.44 | 0.55 | 0.49 | 1702.62 | 200 |
| 2025-09-06 18:21:28 | gemma3 | 2 | Pure instructions prompt | 10 | 7 | 10 | 173 | 0.59 | 0.5 | 0.54 | 1588.4 | 200 |
| 2025-09-06 18:45:23 | gemma3 | 2_1 | Pure instructions prompt v2.1 | 10 | 5 | 10 | 175 | 0.67 | 0.5 | 0.57 | 1432.67 | 200 |
| 2025-09-06 19:04:07 | gemma3 | 2_2 | Pure instructions prompt v2.2 | 3 | 3 | 17 | 177 | 0.5 | 0.15 | 0.23 | 1120.46 | 200 |
| 2025-09-06 19:25:57 | gemma3 | 3 | Prompt with samples | 6 | 2 | 14 | 178 | 0.75 | 0.3 | 0.43 | 1307.63 | 200 |
| 2025-09-06 19:46:18 | gemma3 | 3_1 | Prompt with samples v3.1 | 4 | 4 | 16 | 176 | 0.5 | 0.2 | 0.29 | 1217.62 | 200 |
| 2025-09-06 20:14:42 | gemma3 | 3_2 | Prompt with samples v2.2 | 8 | 85 | 12 | 95 | 0.09 | 0.4 | 0.14 | 1701.67 | 200 |
| 2025-09-06 22:27:34 | gemma3 | 4 | Super simple prompt | 15 | 36 | 5 | 144 | 0.29 | 0.75 | 0.42 | 7969.02 | 200 |
| 2025-09-07 00:07:45 | gemma3 | 5 | Categorization prompt | 16 | 51 | 4 | 129 | 0.24 | 0.8 | 0.37 | 6007.84 | 200 |
