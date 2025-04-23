from faker import Faker
from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv
import os
import boto3
from io import StringIO
from botocore.exceptions import ClientError
import logging

fake = Faker()

# function to generate fake student data
def generate_fake_data(num_records):
    data = []
    #course options from northcoders
    courses = ["Data Engineering", "Software Engineering", "Java Development"]
    
    #cohort start dates
    allowed_cohorts = [
        datetime(2024, 1, 1),
        datetime(2024, 5, 1),
        datetime(2024, 9, 1),
        datetime(2025, 1, 1),
        datetime(2025, 5, 1),
        datetime(2025, 9, 1),
    ]

    for _ in range(num_records):
        # generate name and build varied email usernames based on name parts
        name = fake.name()
        name_parts = name.lower().replace("'", "").split()
        email_patterns = [
            f"{name_parts[0]}.{name_parts[-1]}",
            f"{name_parts[-1]}.{name_parts[0]}",
            f"{name_parts[0]}{fake.random_int(1, 99)}",
            f"{name_parts[0][0]}.{name_parts[-1]}",
            f"{name_parts[0]}_{name_parts[-1]}{fake.random_int(10, 99)}"
        ]
        email_username = fake.random_element(email_patterns)
        email_domain = fake.free_email_domain()
        email = f"{email_username}@{email_domain}"

        # choose a random cohort start date and calculate graduation date 4 months later
        cohort_start = fake.random_element(allowed_cohorts)
        graduation_date = cohort_start + relativedelta(months=4)

        # add the fake record to the list
        data.append({
            "student_id": fake.unique.random_int(min=1, max=999),
            "name": name,
            "course": fake.random_element(courses),
            "cohort": cohort_start.strftime("%Y-%m"),
            "graduation_date": graduation_date.strftime("%Y-%m-%d"),
            "email_address": email
        })

    return data


# def save_to_csv(data, filename):
#     with open(filename, mode="w", newline="", encoding="utf-8") as file:
#         writer = csv.DictWriter(file, fieldnames=data[0].keys())
#         writer.writeheader()
#         writer.writerows(data)

def upload_to_s3(data,bucket,key):
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())
    except ClientError as e:
        logging.error(e)
        return False
    return True

def main():
    bucket = "gdpr-obfuscator-raw"
    object_key = "data.csv"
    data = generate_fake_data(100)
    upload_to_s3(data, bucket, object_key)

if __name__ == "__main__":
    main()

