from typing import List, Any, Callable
from pathlib import Path

import pytest 
import pandas as pd
from unittest.mock import MagicMock

from logging import Logger
from pl_csb_data.data_preparer import DataPreparer

@pytest.fixture(name="create_temp_file")
def create_temp_file_fixture(tmp_path: Path) -> Callable[[str, str, str], Path]:
    def _create_temp_file(filename: str, content: str, encoding: str) -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content, encoding=encoding)
        return file_path
    return _create_temp_file

@pytest.fixture
def mock_logger(mocker):
    return mocker.create_autospec(Logger, instance=True)

@pytest.mark.parametrize(
    "content, expected",
    [
        ("line1\nline2\nline3\n", ["line1", "line2", "line3"]),
        ("line1\rline2\rline3\r", ["line1", "line2", "line3"])
    ]
)
def test_read_text_file_with_various_line_endings(create_temp_file, mock_logger, content: str, expected: List[str]) -> None:
    filename = "test_file.txt"
    file_path = create_temp_file(filename, content, "utf-8")
    preparer = DataPreparer(logger=mock_logger)

    result = preparer._DataPreparer__read_text_file(file_path)
    
    assert result == expected
    
def test_read_text_file_returns_true_not_match(create_temp_file, mock_logger) -> None:
    filename = "test_file.txt"
    content = "line1\fline2\fline3\f"
    file_path = create_temp_file(filename, content, "utf-8")
    preparer = DataPreparer(logger=mock_logger)
    
    result = preparer._DataPreparer__read_text_file(file_path)
    
    result_expected = ["line1", "line2", "line3"]
    assert result != result_expected
    
def test_read_text_file_raises_file_not_found_exception(mock_logger) -> None:
    preparer = DataPreparer(logger=mock_logger)

    result = preparer._DataPreparer__read_text_file("non_existent_file.txt")

    mock_logger.error.assert_called_with("File not found: [Errno 2] No such file or directory: 'non_existent_file.txt'")
    assert result is None
        
def test_read_text_file_raises_unicode_decode_error(create_temp_file, mock_logger) -> None:
    filename = "test_file.txt"
    content = "línea1\nlínea2\nlínea3\n"
    file_path = create_temp_file(filename, content, "latin-1")
    preparer = DataPreparer(logger=mock_logger)

    result = preparer._DataPreparer__read_text_file(file_path)
    
    mock_logger.error.assert_called_with(f"Unicode decode error while reading file {file_path}: 'utf-8' codec can't decode byte 0xed in position 1: invalid continuation byte")
    assert result is None

def test_read_text_file_logs_other_exception(mocker: Any, mock_logger) -> None:
    mock_open = mocker.patch("builtins.open", side_effect=IOError("Unexpected error"))
    preparer = DataPreparer(logger=mock_logger)

    result = preparer._DataPreparer__read_text_file("dummy_file.txt")

    mock_logger.error.assert_called_with("Failed to open file dummy_file.txt: Unexpected error")
    assert result is None
        
def test_prepare_translation_dataset_returns_true_dataframe_match(mocker: Any, mock_logger) -> None:
    mock_polish_train = ["Polish sentence 1", "Polish sentence 2"]
    mock_kashubian_train = ["Kashubian sentence 1", "Kashubian sentence 2"]

    mocker.patch("pl_csb_data.data_preparer.DataPreparer._DataPreparer__read_text_file", side_effect=[mock_polish_train, mock_kashubian_train])

    preparer = DataPreparer(logger=mock_logger)
    df = preparer._DataPreparer__prepare_translation_dataset("dummy_source_path", "dummy_target_path", "pl", "csb")
    
    data_expected = {
        "pl": ["Polish sentence 1", "Polish sentence 2"],
        "csb": ["Kashubian sentence 1", "Kashubian sentence 2"]
    }
    df_expected = pd.DataFrame(data_expected)

    pd.testing.assert_frame_equal(df, df_expected)
