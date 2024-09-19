import os
import pandas as pd
from typing import Tuple

def read_text_file(filename: str) -> list:
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip("\n") for line in file.readlines()]

def prepare_translation_dataset(source_path: str, target_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    kashubian_train = read_text_file(target_path)
    polish_train = read_text_file(source_path)

    train_data = []
    for kashubian, polish in zip(kashubian_train, polish_train):
        train_data.append([kashubian.strip(), polish.strip()])

    train_df = pd.DataFrame(train_data, columns=["pl", "csb"])

    return train_df

def prepare(source_path: str, target_path: str, output_path: str) -> None:
    train_df = prepare_translation_dataset(source_path, target_path)
    train_df.to_csv(output_path, sep="\t")
