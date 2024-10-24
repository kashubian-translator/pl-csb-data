import re
from logging import Logger

import pandas as pd
from tqdm.auto import tqdm
from transformers import NllbTokenizer
from sacremoses import MosesPunctNormalizer


class DataNormalizer:
    __logger: Logger

    def __init__(self, logger):
        self.__logger = logger

    def __check_for_unknown_tokens(self, tokenizer: NllbTokenizer, train_df: pd.DataFrame) -> None:
        try:
            unknown_tokens = [text for text in tqdm(train_df.csb_Latn) if tokenizer.unk_token_id in tokenizer(str(text)).input_ids]
            self.__logger.info(f"Found {len(unknown_tokens)} unknown tokens in the CSB data")

            unknown_tokens = [text for text in tqdm(train_df.pol_Latn) if tokenizer.unk_token_id in tokenizer(str(text)).input_ids]
            self.__logger.info(f"Found {len(unknown_tokens)} unknown tokens in the PL data")
        except Exception as e:
            self.__logger.error(f"Error during unknown token check: {str(e)}")

    def __remove_unprintable_rows(self, train_df: pd.DataFrame) -> pd.DataFrame:
        def printable_filter(row: pd.Series) -> bool:
            # ? Unsure yet about casting to string here because something somewhere in this is a float and throws an error
            # ? Might be useful to check types first but it doesn't seem like a big deal.
            return all(str(cell).isprintable() for cell in row)

        filtered_df = train_df[train_df.apply(printable_filter, axis=1)]

        self.__logger.info(f"Removed {train_df.shape[0] - filtered_df.shape[0]} unprintable rows")

        return filtered_df

    def __remove_rows_with_unknown_tokens(self, tokenizer: NllbTokenizer, train_df: pd.DataFrame, train_df_col: pd.Series) -> pd.DataFrame:
        try:
            rows_to_drop = []
            for id, text in enumerate(train_df_col):
                if tokenizer.unk_token_id in tokenizer(text).input_ids:
                    rows_to_drop.append(id)
            train_df = train_df.drop(rows_to_drop).reset_index(drop=True)
            return train_df
        except Exception as e:
            self.__logger.error(f"Error while removing rows with unknown tokens: {str(e)}")

    def __normalize_translation_dataset(self, train_df: pd.DataFrame) -> pd.DataFrame:
        try:
            mpn = MosesPunctNormalizer(lang="en")
            mpn.substitutions = [
                (re.compile(r), sub) for r, sub in mpn.substitutions
            ]
            source_column = train_df.columns[0]
            target_column = train_df.columns[1]
            train_df[source_column] = train_df[source_column].apply(mpn.normalize)
            train_df[target_column] = train_df[target_column].apply(mpn.normalize)
            return train_df
        except Exception as e:
            self.__logger.error(f"Error during translation dataset normalization: {str(e)}")

    def normalize(self, input_path: str, output_path: str) -> None:
        try:
            tokenizer = NllbTokenizer.from_pretrained("facebook/nllb-200-distilled-600M", additional_special_tokens=["csb_Latn"])
            train_df = pd.read_csv(input_path, sep='\t', index_col=0)

            self.__check_for_unknown_tokens(tokenizer, train_df)

            self.__logger.info("Removing unprintable rows")
            train_df = self.__remove_unprintable_rows(train_df)

            self.__logger.info("Normalizing translation dataset")

            train_df = self.__normalize_translation_dataset(train_df)

            self.__logger.info("Removing rows with unknown tokens")
            train_df = self.__remove_rows_with_unknown_tokens(tokenizer, train_df, train_df[train_df.columns[0]])
            train_df = self.__remove_rows_with_unknown_tokens(tokenizer, train_df, train_df[train_df.columns[1]])

            self.__check_for_unknown_tokens(tokenizer, train_df)
            train_df.to_csv(output_path, sep="\t")
        except Exception as e:
            self.__logger.error(f"Error during normalization process: {str(e)}")
