# GDPR Obfuscator Project

## 📜 Context
The purpose of this project is to create a general-purpose tool to process data being ingested to AWS and intercept personally identifiable information (PII). There is a requirement under [GDPR](https://ico.org.uk/media/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr-1-1.pdf) to ensure that all data containing information that can be used to identify an individual should be anonymised. 

## ✅ Features
- Obfuscates PII fields in CSV files using AWS Lambda
- Triggered automatically on file upload to an S3 bucket
- Stores obfuscated files in a separate destination bucket
- Supports local execution and testing
- Automated CI/CD with GitHub Actions and Terraform
- Email alerting on success/failure via Amazon SNS

## 🧱 Project Structure
```
.
├── data/                      # Sample local CSV data
├── src/
│   ├── obfuscator.py         # Lambda logic for obfuscating PII fields
│   ├── upload_data.py        # Generates and uploads fake data to S3
│   ├── generate_sample.py    # Local script to generate test data
│   └── main.py               # Local obfuscation runner
├── tests/                    # Unit tests with pytest
├── terraform/                # Infrastructure as code (S3, Lambda, IAM, SNS)
├── Makefile                  # Automation commands
└── .github/workflows         # CI/CD via GitHub Actions
```

## 🧪 Test Locally
```bash
make create-environment
make dev-setup
make generate-sample   # Creates local CSV sample in ./data
make test-main-local    # Tests obfuscation with sample
```

## 🚀 Deploy to AWS
Use GitHub Actions on push to `main`:
```yaml
- terraform init
- terraform apply
- run upload_data.py to S3
```

## 🛡️ AWS IAM Setup
To enable Terraform to deploy AWS infrastructure for this project, you need to create an **IAM User** with programmatic access and attach the following **AWS managed policies**:

| Policy Name             | Purpose                          |
|-------------------------|----------------------------------|
| `AmazonS3FullAccess`    | For creating and accessing S3 buckets |
| `AmazonSNSFullAccess`   | For publishing notifications via SNS |
| `AWSLambda_FullAccess`  | For creating and managing Lambda functions |
| `CloudWatchLogsFullAccess` | For viewing and logging Lambda output |
| `IAMFullAccess`         | For creating roles and attaching policies |
| `IAMReadOnlyAccess`     | For inspecting IAM entities during execution |

⚠️ **Note:** You only need `IAMFullAccess` temporarily during setup. For production, apply principle of least privilege.

Once created, set the following secrets in your GitHub repo:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (e.g. `eu-west-2`)
- `SNS_EMAIL` (email address to subscribe to obfuscation result alerts)

## 🔒 GDPR Example Input
```
{
    "file_to_obfuscate": "s3://gdpr-obfuscator-raw/new_data.csv",
    "pii_fields": ["name", "email_address"]
}
```

## 📬 SNS Notifications
- Sends email via SNS when obfuscation **succeeds** or **fails**
- Message contains status and processing time
- You can use a GitHub Actions secret (e.g., `SNS_EMAIL`) for managing your SNS subscription email

## 💡 TODO / Extensions
- Support for JSON & Parquet
- Batch-processing pipeline
- CLI upload tool
- Policy least-privilege refactor

## 🧪 Run All Tests
```bash
make unit-test
```

## 📦 Requirements
- Python 3.11+
- AWS CLI / IAM credentials with access to S3, SNS, Lambda, IAM
- GitHub repository with required secrets set

