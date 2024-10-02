from typing import Any, Callable, Tuple, Optional

import pytest
from unittest.mock import mock_open, MagicMock

from pl_csb_data.data_cleaner import remove_matching_phrases, remove_duplicated_phrases


@pytest.fixture
def mock_open_files(mocker: Any) -> Callable[[str, str], Tuple[MagicMock, MagicMock, MagicMock]]:
    def setup_mocks(polish_content: str, kashubian_content: str) -> Tuple[MagicMock, MagicMock, MagicMock]:
        mock_polish_file = mock_open(read_data=polish_content)
        mock_kashubian_file = mock_open(read_data=kashubian_content)
        mock_temp_polish_file = mock_open()
        mock_temp_kashubian_file = mock_open()

        mocker.patch("builtins.open", side_effect=[
            mock_polish_file.return_value,
            mock_kashubian_file.return_value,
            mock_temp_polish_file.return_value,
            mock_temp_kashubian_file.return_value
        ])

        mock_os_replace = mocker.patch("os.replace")

        return mock_temp_polish_file, mock_temp_kashubian_file, mock_os_replace

    return setup_mocks


@pytest.mark.parametrize(
    "polish_content, kashubian_content, search_phrases, search_in, expected_polish_result, expected_kashubian_result",
    [
        # test case: remove one phrase from each file
        (
            "Długa\nLinia\n",
            "Dłëgô\nLiniô\n",
            ["Długa", "Dłëgô"],
            "both",
            "Linia\n",
            "Liniô\n",
        ),
        # test case: remove multiple phrases from each file
        (
            "Długa bardzo Coś\nLinia\nCoś\n",
            "Dłëgô baro Cos\nLiniô\nCos\n",
            ["Długa", "Cos", "Coś", "Dłëgô"],
            "both",
            "bardzo\nLinia\n",
            "baro\nLiniô\n",
        ),
        # test case: remove a phrase only from polish
        (
            "Długa coś\nLinia\n",
            "Dłëgô coś\nLiniô\n",
            ["coś"],
            "polish",
            "Długa\nLinia\n",
            "Dłëgô coś\nLiniô\n",
        ),
        # test case: remove a phrase only from kashubian
        (
            "Długa coś\nLinia\n",
            "Dłëgô coś\nLiniô\n",
            ["coś"],
            "kashubian",
            "Długa coś\nLinia\n",
            "Dłëgô\nLiniô\n",
        ),
        # test case: remove all short lines
        (
            "Długa\nT\nLinia\n",
            "Dłëgô\nU\nLiniô\n",
            [""],
            "both",
            "Długa\nLinia\n",
            "Dłëgô\nLiniô\n",
        ),
        # test case: remove nothing
        (
            "Długa\nLinia\n",
            "Dłëgô\nLiniô\n",
            ["coś"],
            "both",
            "Długa\nLinia\n",
            "Dłëgô\nLiniô\n",
        ),
        # test case: empty files
        (
            "",
            "",
            ["coś"],
            "both",
            "",
            "",
        ),
    ]
)
def test_remove_matching_phrases_returns_true_file_content_match(mock_open_files, polish_content: str, kashubian_content: str, search_phrases: list[str], search_in: str, expected_polish_result: Optional[str], expected_kashubian_result: Optional[str]) -> None:
    mock_temp_polish_file, mock_temp_kashubian_file, mock_os_replace = mock_open_files(polish_content, kashubian_content)

    remove_matching_phrases("mock_polish_path.txt", "mock_kashubian_path.txt", search_phrases, search_in)

    if expected_polish_result:
        for line in expected_polish_result.splitlines():
            mock_temp_polish_file().write.assert_any_call(line + "\n")
    else:
        mock_temp_polish_file().write.assert_not_called()

    if expected_kashubian_result:
        for line in expected_kashubian_result.splitlines():
            mock_temp_kashubian_file().write.assert_any_call(line + "\n")
    else:
        mock_temp_kashubian_file().write.assert_not_called()

    mock_os_replace.assert_any_call("mock_polish_path.txt.tmp", "mock_polish_path.txt")
    mock_os_replace.assert_any_call("mock_kashubian_path.txt.tmp", "mock_kashubian_path.txt")


def test_remove_matching_phrases_raises_value_error_exception():
    with pytest.raises(ValueError, match="search_in parameter must be 'polish', 'kashubian', or 'both'"):
        remove_matching_phrases("mock_polish_path.txt", "mock_kashubian_path.txt", ["coś"], search_in="invalid")


@pytest.mark.parametrize(
    "polish_content, kashubian_content, expected_polish_result, expected_kashubian_result",
    [
        # test case: remove one duplicate
        (
            "Długa\nDługa\n",
            "Dłëgô\nDłëgô\n",
            ["Długa\n"],
            ["Dłëgô\n"]
        ),
        # test case: unique line between two duplicates
        (
            "Długa\nLinia\nDługa\n",
            "Dłëgô\nLiniô\nDłëgô\n",
            ["Długa\n", "Linia\n"],
            ["Dłëgô\n", "Liniô\n"]
        ),
        # test case: no duplicates to remove
        (
            "Długa\nLinia\n",
            "Dłëgô\nLiniô\n",
            ["Długa\n", "Linia\n"],
            ["Dłëgô\n", "Liniô\n"]
        ),
        # test case: empty files
        (
            "",
            "",
            [],
            []
        ),
    ]
)
def test_remove_duplicated_phrases_returns_true_files_content_written(mock_open_files, polish_content: str, kashubian_content: str, expected_polish_result: list[str], expected_kashubian_result: list[str]) -> None:
    mock_temp_polish_file, mock_temp_kashubian_file, mock_os_replace = mock_open_files(polish_content, kashubian_content)

    remove_duplicated_phrases("mock_polish_path.txt", "mock_kashubian_path.txt")

    mock_temp_polish_file().writelines.assert_called_once_with(expected_polish_result)
    mock_temp_kashubian_file().writelines.assert_called_once_with(expected_kashubian_result)

    mock_os_replace.assert_any_call("mock_polish_path.txt.tmp", "mock_polish_path.txt")
    mock_os_replace.assert_any_call("mock_kashubian_path.txt.tmp", "mock_kashubian_path.txt")
