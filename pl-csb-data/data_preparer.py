import os
import pandas as pd
from typing import Tuple

def read_text_file(filename: str) -> list:
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip("\n") for line in file.readlines()]

def prepare_translation_dataset(data_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    kashubian_train = read_text_file(os.path.join(data_path, "train.trg"))
    polish_train = read_text_file(os.path.join(data_path, "train.src"))

    train_data = []
    for kashubian, polish in zip(kashubian_train, polish_train):
        train_data.append([kashubian.strip(), polish.strip()])

    train_df = pd.DataFrame(train_data, columns=["pl", "csb"])

    return train_df

def prepare() -> None:
    data_path = "data"
    train_df = prepare_translation_dataset(f"{data_path}/input")
    train_df.to_csv(f"{data_path}/output/train.tsv", sep="\t")
