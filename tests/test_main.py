from unittest.mock import patch, mock_open
from src import main


@patch("src.main.obfuscate_csv")
@patch("builtins.open", new_callable=mock_open, read_data="name,email\nJohn,john@example.com\n")
@patch("argparse.ArgumentParser.parse_args")
def test_main_fully_mocked(mock_args, mock_open_file, mock_obfuscate):
    mock_args.return_value.input = "dummy.csv"
    mock_args.return_value.output = "obfuscated.csv"
    mock_args.return_value.fields = ["name", "email"]

    mock_obfuscate.return_value = "name,email\n***,***\n"

    main.main()

    mock_open_file.assert_any_call("dummy.csv", "r")
    mock_open_file.assert_any_call("obfuscated.csv", "w")
    mock_obfuscate.assert_called_once_with("name,email\nJohn,john@example.com\n", ["name", "email"])
    mock_open_file().write.assert_called_once_with("name,email\n***,***\n")
