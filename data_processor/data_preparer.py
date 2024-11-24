from logging import Logger
from typing import Optional

import pandas as pd


class DataPreparer:
    __logger: Logger

    def __init__(self, logger: Logger):
        self.__logger = logger

    def __read_text_file(self, filename: str) -> Optional[list]:
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return [line.strip("\n") for line in file.readlines()]
        except FileNotFoundError as e:
            self.__logger.error(f"File not found: {e}")
            return None
        except UnicodeDecodeError as e:
            self.__logger.error(f"Unicode decode error while reading file {filename}: {e}")
            return None
        except Exception as e:
            self.__logger.error(f"Failed to open file {filename}: {e}")
            return None

    def __prepare_translation_dataset(self, source_path: str, target_path: str, source_lang: str, target_lang: str) -> Optional[pd.DataFrame]:
        self.__logger.info(f"Preparing translation dataset: {source_lang} → {target_lang}")
        source_train = self.__read_text_file(source_path)

        if source_train is None:
            self.__logger.error("Source file reading failed, aborting dataset preparation")
            return None

        target_train = self.__read_text_file(target_path)

        if target_train is None:
            self.__logger.error("Target file reading failed, aborting dataset preparation")
            return None

        if len(source_train) != len(target_train):
            self.__logger.error("Source and target files have different lengths, aborting dataset preparation")
            return None

        try:
            train_data = [[source.strip(), target.strip()] for source, target in zip(source_train, target_train)]
            train_df = pd.DataFrame(train_data, columns=[source_lang, target_lang])
        except Exception as e:
            self.__logger.error(f"Error while preparing DataFrame: {e}")
            return None

        return train_df

    def prepare(self, source_path: str, target_path: str, output_path: str, source_lang: str, target_lang: str) -> None:
        self.__logger.info("Starting data preparation process")

        try:
            train_df = self.__prepare_translation_dataset(source_path, target_path, source_lang, target_lang)
            if train_df is None:
                self.__logger.error("Dataset preparation failed, model ready file won't be written")
                return

            train_df.to_csv(output_path, sep="\t")
            self.__logger.info(f"Data successfully written to {output_path}")
        except Exception as e:
            self.__logger.error(f"Failed to save the prepared data: {e}")
