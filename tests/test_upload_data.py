from src.upload_data import generate_fake_data, upload_to_s3, main 
import logging
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

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

@patch("src.upload_data.boto3.client")
def test_upload_to_s3_success(mock_boto_client):
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    data = generate_fake_data(1)
    result = upload_to_s3(data, "test-bucket", "test.csv")

    assert result is True
    mock_s3.put_object.assert_called_once()

@patch("src.upload_data.boto3.client")
@patch("src.upload_data.logging")
def test_upload_to_s3_failure_logs_error(mock_logging, mock_boto_client):
    mock_s3 = MagicMock()
    mock_s3.put_object.side_effect = ClientError(
    error_response={"Error": {"Code": "500", "Message": "Simulated S3 error"}},
    operation_name="PutObject"
)
    mock_boto_client.return_value = mock_s3

    data = generate_fake_data(1)
    result = upload_to_s3(data, "test-bucket", "test.csv")

    assert result is False
    mock_logging.error.assert_called_once()

@patch("src.upload_data.upload_to_s3")
def test_main_executes_upload(mock_upload):
    main()
    mock_upload.assert_called_once()
