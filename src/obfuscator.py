import csv
from io import StringIO
import boto3
import logging
import json

s3_client = boto3.client('s3')

def obfuscate_fields(row, pii_fields):
    for field in pii_fields:
        if field in row:
            row[field] = "***"
    return row

def parse_s3_uri(uri):
    parts = uri.replace("s3://", "").split("/", 1)
    return parts[0], parts[1]

def obfuscate_csv(content, pii_fields):
    input_buffer = StringIO(content)
    output_buffer = StringIO()

    reader = csv.DictReader(input_buffer)
    writer = csv.DictWriter(output_buffer, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        obfuscated = obfuscate_fields(row, pii_fields)
        writer.writerow(obfuscated)

    return output_buffer.getvalue()

def download_csv_from_s3(bucket, key):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read().decode("utf-8")

def upload_to_s3(bucket, key, content):
    try:
        s3_client.put_object(Bucket=bucket, Key=key, Body=content)
        return True
    except Exception as e:
        logging.error(e)
        return False

def lambda_handler(event, context):
    try:
        # Check if it's a direct payload
        if "file_to_obfuscate" in event or ("body" in event and "file_to_obfuscate" in json.loads(event["body"])):
            if "body" in event:
                payload = json.loads(event["body"])
            else:
                payload = event

            bucket, key = parse_s3_uri(payload["file_to_obfuscate"])
            pii_fields = payload["pii_fields"]
        else:
            # Handle S3 event payload
            records = event.get("Records", [])
            if not records:
                raise Exception("No records found in event")

            s3_info = records[0]["s3"]
            bucket = s3_info["bucket"]["name"]
            key = s3_info["object"]["key"]

            pii_fields = ["name", "email_address"]

        csv_content = download_csv_from_s3(bucket, key)
        obfuscated_csv = obfuscate_csv(csv_content, pii_fields)

        output_key = f"{key}"
        upload_success = upload_to_s3("gdpr-obfuscator-obfuscated", output_key, obfuscated_csv)

        if not upload_success:
            raise Exception("Upload failed")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "File obfuscated and uploaded",
                "output_s3_path": f"s3://gdpr-obfuscator-obfuscated/{output_key}"
            })
        }

    except Exception as e:
        logging.error(f"Lambda error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
