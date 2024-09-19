import re
import pandas as pd

from tqdm.auto import tqdm
from transformers import NllbTokenizer
from sacremoses import MosesPunctNormalizer

def check_for_unknown_tokens(tokenizer: NllbTokenizer, train_df: pd.DataFrame) -> None:
    unknown_tokens = [text for text in tqdm(train_df.csb) if tokenizer.unk_token_id in tokenizer(str(text)).input_ids]
    print(f"Found {len(unknown_tokens)} unknown tokens in the CSB data")

    unknown_tokens = [text for text in tqdm(train_df.pl) if tokenizer.unk_token_id in tokenizer(str(text)).input_ids]
    print(f"Found {len(unknown_tokens)} unknown tokens in the PL data")

def remove_rows_with_unknown_tokens(tokenizer: NllbTokenizer, train_df: pd.DataFrame, train_df_col: pd.Series) -> pd.DataFrame:
    rows_to_drop = []
    
    for id, text in enumerate(train_df_col):
        if tokenizer.unk_token_id in tokenizer(text).input_ids:
            rows_to_drop.append(id)
    
    train_df = train_df.drop(rows_to_drop).reset_index(drop=True)
    
    return train_df

def normalize_translation_dataset(train_df: pd.DataFrame) -> None:
    mpn = MosesPunctNormalizer(lang="en")
    mpn.substitutions = [
        (re.compile(r), sub) for r, sub in mpn.substitutions
    ]
    
    train_df["csb"] = train_df.csb.apply(mpn.normalize)
    train_df["pl"] = train_df.pl.apply(mpn.normalize)

    return train_df

def normalize(input_path: str, output_path: str) -> None:
    tokenizer = NllbTokenizer.from_pretrained("facebook/nllb-200-distilled-600M", additional_special_tokens=["csb_Latn"])
    
    train_df = pd.read_csv(input_path, sep='\t', index_col=0)

    check_for_unknown_tokens(tokenizer, train_df)

    print("Normalizing translation dataset")
    train_df = normalize_translation_dataset(train_df)

    print("Removing rows with unknown tokens")
    train_df = remove_rows_with_unknown_tokens(tokenizer, train_df, train_df.csb)
    train_df = remove_rows_with_unknown_tokens(tokenizer, train_df, train_df.pl)

    check_for_unknown_tokens(tokenizer, train_df)

    train_df.to_csv(output_path, sep="\t")
