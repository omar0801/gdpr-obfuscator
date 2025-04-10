from src.obfuscator.fake_data import generate_fake_data
import os
from src.obfuscator.fake_data import generate_fake_data, save_to_csv

def test_returns_list_of_dicts():
    data = generate_fake_data(1)
    assert isinstance(data, list)
    assert isinstance(data[0], dict)

def test_expected_fields():
    data = generate_fake_data(1)
    row = data[0]
    expected = {'student_id',
                'name',
                'course',
                'cohort',
                'graduation_date',
                'email_address'}
    assert set(row.keys()) == expected

def test_generated_data_has_non_static_values():
    data = generate_fake_data(2)
    assert data[0] != data[1]

def test_student_ids_are_unique():
    data = generate_fake_data(50)
    ids = [row["student_id"] for row in data]
    assert len(ids) == len(set(ids))

def test_email_contains_parts_of_name():
    data = generate_fake_data(1)
    name = data[0]["name"].lower().replace("'", "")
    name_parts = name.split()
    email_username = data[0]["email_address"].split("@")[0].lower()

    assert any(part in email_username for part in name_parts)


def test_email_uses_common_domain():
    data = generate_fake_data(1)
    domain = data[0]["email_address"].split("@")[1]
    common_domains = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "live.com", "aol.com", "icloud.com"}
    assert domain in common_domains

def test_course_is_limited_to_allowed_options():
    data = generate_fake_data(30)
    allowed_courses = {"Data Engineering", "Software Engineering", "Java Development"}

    for row in data:
        assert row["course"] in allowed_courses

from datetime import datetime

def test_graduation_date_is_4_months_after_cohort():
    data = generate_fake_data(10)
    for row in data:
        cohort = datetime.strptime(row["cohort"], "%Y-%m")
        grad = row["graduation_date"]
        if isinstance(grad, str):
            grad = datetime.strptime(grad, "%Y-%m-%d")

        delta_months = (grad.year - cohort.year) * 12 + (grad.month - cohort.month)
        assert delta_months == 4

def test_save_to_csv_creates_file(tmp_path):
    file_path = tmp_path / "output.csv"
    data = generate_fake_data(5)
    save_to_csv(data, file_path)

    assert os.path.exists(file_path)