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

# Data Sources
https://github.com/Helsinki-NLP/Tatoeba-Challenge
