from typing import List, Any, Callable
from pathlib import Path

import pytest 
import pandas as pd

from pl_csb_data.data_preparer import read_text_file, prepare_translation_dataset

@pytest.fixture(name="create_temp_file")
def create_temp_file_fixture(tmp_path: Path) -> Callable[[str, str, str], Path]:
    def _create_temp_file(filename: str, content: str, encoding: str) -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content, encoding=encoding)
        return file_path
    return _create_temp_file

@pytest.mark.parametrize(
    "content, expected",
    [
        ("line1\nline2\nline3\n", ["line1", "line2", "line3"]),
        ("line1\rline2\rline3\r", ["line1", "line2", "line3"])
    ]
)
def test_read_text_file_with_various_line_endings(create_temp_file, content: str, expected: List[str]) -> None:
    filename = "test_file.txt"
    
    file_path = create_temp_file(filename, content, "utf-8")
    
    result = read_text_file(file_path)
    
    assert result == expected
    
def test_read_text_file_returns_true_not_match(create_temp_file) -> None:
    filename = "test_file.txt"
    content = "line1\fline2\fline3\f"
    
    file_path = create_temp_file(filename, content, "utf-8")
    
    result = read_text_file(file_path)
    
    result_expected = ["line1", "line2", "line3"]
    assert result != result_expected
    
def test_read_text_file_raises_file_not_found_exception() -> None:
    with pytest.raises(FileNotFoundError):
        read_text_file("non_existent_file.txt")
        
def test_read_text_file_raises_unicode_decode_error(create_temp_file) -> None:
    filename = "test_file.txt"
    content = "línea1\nlínea2\nlínea3\n"
    
    file_path = create_temp_file(filename, content, "latin-1")
    
    with pytest.raises(UnicodeDecodeError):
        read_text_file(file_path)
        
def test_prepare_translation_dataset_returns_true_dataframe_match(mocker : Any) -> None:
    mock_polish_train = ["Polish sentence 1", "Polish sentence 2"]
    mock_kashubian_train = ["Kashubian sentence 1", "Kashubian sentence 2"]

    mocker.patch("pl_csb_data.data_preparer.read_text_file", side_effect=[mock_kashubian_train, mock_polish_train])

    df = prepare_translation_dataset("dummy_source_path", "dummy_target_path", "pl", "csb")
    
    data_expected = {
        "pl": ["Polish sentence 1", "Polish sentence 2"],
        "csb": ["Kashubian sentence 1", "Kashubian sentence 2"]
    }
    df_expected = pd.DataFrame(data_expected)

    pd.testing.assert_frame_equal(df, df_expected)
