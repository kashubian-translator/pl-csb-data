import pandas as pd
from typing import Tuple


def read_text_file(filename: str) -> list:
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip("\n") for line in file.readlines()]


def prepare_translation_dataset(source_path: str, target_path: str, source_lang: str, target_lang: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    source_train = read_text_file(source_path)
    target_train = read_text_file(target_path)

    train_data = []
    for source, target in zip(target_train, source_train):
        train_data.append([source.strip(), target.strip()])

    train_df = pd.DataFrame(train_data, columns=[source_lang, target_lang])

    return train_df


def prepare(source_path: str, target_path: str, output_path: str, source_lang: str, target_lang: str) -> None:
    train_df = prepare_translation_dataset(source_path, target_path, source_lang, target_lang)
    train_df.to_csv(output_path, sep="\t")
