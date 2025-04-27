from src.upload_data import generate_fake_data
from src.generate_sample import save_to_csv, main
import os
import csv
import pytest

@pytest.fixture
def sample_path():
    return "data/test_sample.csv"

def test_generate_and_save_csv_creates_file(sample_path):
    data = generate_fake_data(5)
    save_to_csv(data, sample_path)

    assert os.path.exists(sample_path)

    with open(sample_path) as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 5
        assert "name" in reader[0]
        assert "email_address" in reader[0]

    os.remove(sample_path)

def test_main_creates_default_sample_file():
    main()

    assert os.path.exists("data/sample.csv")

    with open("data/sample.csv") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) > 0
        assert "name" in reader[0]
        assert "email_address" in reader[0]

    os.remove("data/sample.csv")
