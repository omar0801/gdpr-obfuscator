from src.obfuscator import obfuscate_fields , parse_s3_uri , obfuscate_csv , download_csv_from_s3 , upload_to_s3 , lambda_handler
from unittest.mock import patch, MagicMock
import json



class TestObfuscateFields:

    def test_single_field_obfuscated(self):
        row = {"name": "John"}
        pii = ["name"]
        result = obfuscate_fields(row, pii)
        assert result["name"] == "***"

    def test_non_pii_field_untouched(self):
        row = {"name": "John", "course": "Python"}
        pii = ["name"]
        result = obfuscate_fields(row, pii)
        assert result["course"] == "Python"

    def test_multiple_fields_obfuscated(self):
        row = {
            "name": "Alice",
            "email_address": "alice@example.com",
            "course": "Data Engineering"
        }
        pii = ["name", "email_address"]
        result = obfuscate_fields(row, pii)
        assert result["name"] == "***"
        assert result["email_address"] == "***"
        assert result["course"] == "Data Engineering"

class TestParseS3Uri():

    def test_parse_s3_uri_extracts_bucket_and_key(self):
        s3_path = "s3://gdpr-obfuscator-raw/fake_student_data.csv"
        bucket, key = parse_s3_uri(s3_path)
        assert bucket == "gdpr-obfuscator-raw"
        assert key == "fake_student_data.csv"

class TestObfuscateCsv():
    def test_obfuscate_csv_single_field(self):
        input_csv = "name,email_address\nJohn,john@example.com\n"
        pii = ["name"]

        result = obfuscate_csv(input_csv, pii)
        print(f"==>> result: {result}")

        assert "***" in result
        assert "john@example.com" in result

class TestDownloadCSV:
    @patch("src.obfuscator.s3_client.get_object")
    def test_download_csv_returns_string(self, mock_get_object):
        mock_get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=b"name,email\nJohn,john@example.com"))
        }

        content = download_csv_from_s3("fake-bucket", "fake.csv")
        assert isinstance(content, str)
        assert "John" in content

class TestUploadCSV:
    @patch("src.obfuscator.s3_client.put_object")
    def test_upload_to_s3_success(self, mock_put):
        result = upload_to_s3("test-bucket", "output.csv", "some,data\nhere")
        mock_put.assert_called_once()
        assert result is True

    @patch("src.obfuscator.s3_client.put_object")
    @patch("src.obfuscator.logging")
    def test_upload_to_s3_failure_logs_error(self, mock_logging, mock_put):
        mock_put.side_effect = Exception("S3 failed to upload")

        result = upload_to_s3("bucket", "key", "content")

        assert result is False
        mock_logging.error.assert_called_once()

class TestLambdaHandler:
    @patch("src.obfuscator.upload_to_s3")
    @patch("src.obfuscator.obfuscate_csv")
    @patch("src.obfuscator.download_csv_from_s3")
    @patch("src.obfuscator.parse_s3_uri")
    def test_lambda_handler_success(
        self,
        mock_parse_uri,
        mock_download_csv,
        mock_obfuscate_csv,
        mock_upload
    ):
        # Arrange
        mock_parse_uri.return_value = ("test-bucket", "test.csv")
        mock_download_csv.return_value = "name,email\nJohn,john@example.com\n"
        mock_obfuscate_csv.return_value = "name,email\n***,john@example.com\n"
        mock_upload.return_value = True

        event = {
            "file_to_obfuscate": "s3://test-bucket/test.csv",
            "pii_fields": ["name"]
        }

        # Act
        response = lambda_handler(event, None)

        # Assert
        assert response["statusCode"] == 200
        assert "output_s3_path" in response["body"]
        mock_parse_uri.assert_called_once()
        mock_download_csv.assert_called_once()
        mock_obfuscate_csv.assert_called_once()
        mock_upload.assert_called_once()

    @patch("src.obfuscator.upload_to_s3")
    @patch("src.obfuscator.obfuscate_csv")
    @patch("src.obfuscator.download_csv_from_s3")
    @patch("src.obfuscator.parse_s3_uri")
    def test_lambda_handler_with_wrapped_event(
    self,
    mock_parse_uri,
    mock_download_csv,
    mock_obfuscate_csv,
    mock_upload
):
        mock_parse_uri.return_value = ("bucket", "file.csv")
        mock_download_csv.return_value = "name,email\nJohn,john@example.com"
        mock_obfuscate_csv.return_value = "name,email\n***,john@example.com"
        mock_upload.return_value = True

        event = {
            "body": json.dumps({
                "file_to_obfuscate": "s3://bucket/file.csv",
                "pii_fields": ["name"]
            })
        }

        response = lambda_handler(event, None)

        assert response["statusCode"] == 200
        assert "output_s3_path" in response["body"]

    @patch("src.obfuscator.upload_to_s3")
    @patch("src.obfuscator.obfuscate_csv")
    @patch("src.obfuscator.download_csv_from_s3")
    @patch("src.obfuscator.parse_s3_uri")
    @patch("src.obfuscator.logging")
    def test_lambda_handler_upload_failure_logs_error(
    self,
    mock_logging,
    mock_parse_uri,
    mock_download_csv,
    mock_obfuscate_csv,
    mock_upload
):
        mock_parse_uri.return_value = ("bucket", "file.csv")
        mock_download_csv.return_value = "some,data\n"
        mock_obfuscate_csv.return_value = "some,obfuscated\n"
        mock_upload.return_value = False  # force upload failure

        event = {
            "file_to_obfuscate": "s3://bucket/file.csv",
            "pii_fields": ["some"]
        }

        response = lambda_handler(event, None)

        assert response["statusCode"] == 500
        assert "error" in response["body"]
        mock_logging.error.assert_called()

    @patch("src.obfuscator.upload_to_s3")
    @patch("src.obfuscator.obfuscate_csv")
    @patch("src.obfuscator.download_csv_from_s3")
    def test_lambda_handler_s3_event(
        self,
        mock_download_csv,
        mock_obfuscate_csv,
        mock_upload
    ):
        mock_download_csv.return_value = "name,email\nJohn,john@example.com"
        mock_obfuscate_csv.return_value = "name,email\n***,john@example.com"
        mock_upload.return_value = True

        event = {
            "Records": [{
                "s3": {
                    "bucket": {"name": "gdpr-obfuscator-raw"},
                    "object": {"key": "test.csv"}
                }
            }]
        }

        response = lambda_handler(event, None)

        assert response["statusCode"] == 200
        assert "output_s3_path" in response["body"]

    def test_lambda_handler_s3_event_missing_records(self):
        event = {}  # no "Records" key

        response = lambda_handler(event, None)

        assert response["statusCode"] == 500
        assert "No records found in event" in response["body"]

