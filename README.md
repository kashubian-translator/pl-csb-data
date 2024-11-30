# Project Setup

## Prerequisites
It is recommended to create a Python virtual environment before proceeding. You can read more about it [here](https://docs.python.org/3/library/venv.html).

## Installation
1. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2. **Install Autopep8 Pre-commit Hook**:
    ```bash
    pre-commit install
    ```

# Data Directory Structure

The structure of the `data` directory is organised as follows:

- **`0_raw`**  
  Contains uncleaned data fetched from various data sources with standardised extensions: either .csb.txt or .pl.txt. 
  This is the initial state of the dataset.

- **`1_cleaned`**  
  Holds cleaned data, prepared either through scripts, manual correction, or a combination of both.

- **`2_split`**  
  Includes datasets divided into three subsets:  
  - **Training Set**  
  - **Validation Set**  
  - **Test Set**  
  For more details, see the **Datasets** section.

- **`3_preprocessed`**  
  Contains data preprocessed and formatted to be directly fed into the model.

# Data Processing
To prepare and normalize data in the `data/input` directory and save the processed data in the `data/output` directory, run:
```bash
python data_processor
```

# Data Scraping
To scrape or clean scraped data, run the individual `Python` scripts in the `scrapers` directory.

# Running Tests
To execute tests, run:
```bash
pytest test
```

# Datasets

## Train
Used to train the model.

## Validation
Used to calculate loss after each training epoch and check `BLEU` and `chrF++` metrics during development

## Validation Debug
Used to quickly check `BLEU` and `chrF++` metrics during debugging.

## Test
Used to check `BLEU` and `chrF++` metrics in the final model evaluation.

# Data Sources
https://github.com/Helsinki-NLP/Tatoeba-Challenge
https://opus.nlpl.eu
https://sloworz.org
https://kaszebe.org
https://odmiana.net/
Book "The Life and Adventures of Remus"
