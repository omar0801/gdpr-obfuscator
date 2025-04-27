import argparse
from src.obfuscator import obfuscate_csv

def main():
    parser = argparse.ArgumentParser(description="Obfuscate PII fields in a local CSV file")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to save obfuscated CSV")
    parser.add_argument("--fields", required=True, nargs="+", help="PII fields to obfuscate")

    args = parser.parse_args()

    with open(args.input, "r") as f:
        content = f.read()

    result = obfuscate_csv(content, args.fields)

    with open(args.output, "w") as f:
        f.write(result)

    print(f"✅ Obfuscated file saved to {args.output}")

if __name__ == "__main__":
    main()
