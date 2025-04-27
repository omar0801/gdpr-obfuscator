
from src.upload_data import generate_fake_data
import csv
import os

def save_to_csv(data, filename="data/sample.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Sample CSV written to {filename}")

def main():
    data = generate_fake_data(20)
    save_to_csv(data)

if __name__ == "__main__":
    main()
