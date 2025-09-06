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


