from typing import Any

import pytest 
import pandas as pd
from transformers import NllbTokenizer
from unittest.mock import MagicMock

from logging import Logger
from pl_csb_data.data_normalizer import DataNormalizer

@pytest.fixture
def mock_nllb_tokenizer(mocker : Any) -> MagicMock:
    mock_nllb_tokenizer = mocker.MagicMock(spec=NllbTokenizer)
    
    mock_nllb_tokenizer.unk_token_id = 0
    
    def mock_tokenize(text: str) -> MagicMock:
        if text == "unknown_token":
            return mocker.MagicMock(input_ids=[0, 1, 2])
        else:
            return mocker.MagicMock(input_ids=[1, 2, 3])
    
    mock_nllb_tokenizer.side_effect = mock_tokenize
    
    return mock_nllb_tokenizer

@pytest.fixture
def mock_moses_punct_normalizer(mocker):
    mock_mpn = mocker.patch("pl_csb_data.data_normalizer.MosesPunctNormalizer", autospec=True)
    mock_instance = mock_mpn.return_value

    mock_instance.substitutions = []  
    
    def normalize_side_effect(text):
        if text is None:
            return text
        stripped_text = text.strip()
        return f"{stripped_text}_normalized" if stripped_text else "_normalized"

    mock_instance.normalize.side_effect = normalize_side_effect

    return mock_instance

@pytest.fixture
def mock_logger(mocker):
    return mocker.create_autospec(Logger, instance=True)

@pytest.mark.parametrize(
    "input_data, csb_expected_unknown_tokens, pl_expected_unknown_tokens",
    [
        # test case: unknown tokens amidst known tokens
        ({"csb_Latn": ["unknown_token", "unknown_token", "known_token"],
        "pol_Latn": ["known_token", "known_token", "unknown_token"]},
        2,
        1),
        # test case: no unknown tokens found
        ({"csb_Latn": ["known_token", "known_token", "known_token"],
        "pol_Latn": ["known_token", "known_token", "known_token"]},
        0,
        0),
        # test case: all unknown tokens
        ({"csb_Latn": ["unknown_token", "unknown_token", "unknown_token"],
        "pol_Latn": ["unknown_token", "unknown_token", "unknown_token"]},
        3,
        3)
    ]
)
def test_check_for_unknown_tokens_returns_true_found_tokens(mock_nllb_tokenizer, capsys, mock_logger, input_data: dict[str, list[str]], csb_expected_unknown_tokens: int, pl_expected_unknown_tokens: int) -> None:
    train_df = pd.DataFrame(input_data)
    normalizer = DataNormalizer(logger=mock_logger)
    normalizer._DataNormalizer__check_for_unknown_tokens(mock_nllb_tokenizer, train_df)
    output = capsys.readouterr().out.rstrip()
    
    mock_logger.info.assert_any_call(f"Found {csb_expected_unknown_tokens} unknown tokens in the CSB data")
    mock_logger.info.assert_any_call(f"Found {pl_expected_unknown_tokens} unknown tokens in the PL data")

@pytest.mark.parametrize(
    "input_data, column_name, expected_output_data",
    [
        # test case 1: removes unknown tokens amidst known tokens
        (
            {"csb": ["known_token", "unknown_token", "known_token"], "pl": ["known_token", "unknown_token", "known_token"]},
            "csb",
            {"csb": ["known_token", "known_token"], "pl": ["known_token", "known_token"]}
        ),
        # test case 2: no unknown tokens to remove
        (
            {"csb": ["known_token", "known_token"], "pl": ["known_token", "known_token"]},
            "pl",
            {"csb": ["known_token", "known_token"], "pl": ["known_token", "known_token"]}
        ),
        # test case 3: all unknown tokens to remove
        (
            {"csb": ["unknown_token", "unknown_token"], "pl": ["unknown_token", "unknown_token"]},
            "csb",
            {"csb": [], "pl": []}
        ),
    ]
)  
def test_remove_rows_with_unknown_tokens_returns_true_dataframe_match(mock_nllb_tokenizer, mock_logger, input_data: dict[str, list[str]], column_name: str, expected_output_data: dict[str, list[Any]]) -> None:
    train_df = pd.DataFrame(input_data)
    train_df_col = train_df[column_name]
    normalizer = DataNormalizer(logger=mock_logger)
    result_df = normalizer._DataNormalizer__remove_rows_with_unknown_tokens(mock_nllb_tokenizer, train_df, train_df_col)
    
    expected_df = pd.DataFrame(expected_output_data).astype({"csb": "object", "pl": "object"}).reset_index(drop=True)
    
    pd.testing.assert_frame_equal(result_df, expected_df)

@pytest.mark.parametrize(
    "input_data, expected_data",
    [
        # test case 1: normalizes all strings
        (
            {"csb": ["Line 1", "Line 2"], "pl": ["Linia 1", "Linia 2"]},
            {"csb": ["Line 1_normalized", "Line 2_normalized"], "pl": ["Linia 1_normalized", "Linia 2_normalized"]}
        ),
        # test case 2: empty input
        (
            {"csb": ["", ""], "pl": ["", ""]},
            {"csb": ["_normalized", "_normalized"], "pl": ["_normalized", "_normalized"]}
        ),
        # test case 2: mixed input with empty and non-empty strings
        (
            {"csb": ["Line 1", "  "], "pl": ["Linia 1", "    "]},
            {"csb": ["Line 1_normalized", "_normalized"], "pl": ["Linia 1_normalized", "_normalized"]}
        ),
    ]
)
def test_normalize_translation_dataset_returns_true_dataframe_match_call_count_match(mock_moses_punct_normalizer, mock_logger, input_data: str, expected_data: str) -> None:
    input_df = pd.DataFrame(input_data)
    normalizer = DataNormalizer(logger=mock_logger)
    normalized_df = normalizer._DataNormalizer__normalize_translation_dataset(input_df)
    
    expected_df = pd.DataFrame(expected_data)
    
    pd.testing.assert_frame_equal(normalized_df, expected_df)
