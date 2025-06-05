import os
import csv
import json

class DataProcessor:
    def __init__(self, data_source_path="data.csv"):
        self.data_source_path = data_source_path
        self.processed_data = []

    def _load_data(self):
        """Loads data from the specified CSV file."""
        if not os.path.exists(self.data_source_path):
            print(f"Error: Data file not found at {self.data_source_path}")
            return False
        try:
            with open(self.data_source_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.raw_data = [row for row in reader]
            print(f"Successfully loaded {len(self.raw_data)} rows from {self.data_source_path}")
            return True
        except Exception as e:
            print(f"Failed to load data: {e}")
            return False

    def process_records(self):
        """Processes each record in the loaded data."""
        if not self._load_data():
            return

        for record in self.raw_data:
            # Example processing: convert 'value' to int if exists
            try:
                if 'value' in record:
                    record['value'] = int(record['value'])
                self.processed_data.append(record)
            except ValueError:
                print(f"Warning: Could not convert value in record: {record}")
                self.processed_data.append(record) # Append even if conversion fails

        print(f"Processed {len(self.processed_data)} records.")

    def save_processed_data(self, output_path="processed_data.json"):
        """Saves the processed data to a JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.processed_data, f, indent=4, ensure_ascii=False)
            print(f"Processed data saved to {output_path}")
        except Exception as e:
            print(f"Failed to save processed data: {e}")

if __name__ == "__main__":
    # Create a dummy CSV file for testing
    dummy_data = [
        {"id": "1", "name": "Alice", "value": "100"},
        {"id": "2", "name": "Bob", "value": "200"},
        {"id": "3", "name": "Charlie", "value": "abc"}, # This will cause a ValueError
        {"id": "4", "name": "David", "value": "400"}
    ]
    with open("data.csv", "w", newline='', encoding='utf-8') as f:
        fieldnames = dummy_data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dummy_data)
    print("Dummy data.csv created.")

    processor = DataProcessor()
    processor.process_records()
    processor.save_processed_data()
