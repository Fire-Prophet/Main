import csv
import json
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, data_source_path, report_output_dir="reports"):
        self.data_source_path = data_source_path
        self.report_output_dir = report_output_dir
        if not os.path.exists(self.report_output_dir):
            os.makedirs(self.report_output_dir)
            print(f"Created report output directory: {self.report_output_dir}")

    def _load_data(self):
        """Loads data from CSV or JSON based on file extension."""
        if not os.path.exists(self.data_source_path):
            print(f"Error: Data source not found at {self.data_source_path}")
            return None

        file_extension = os.path.splitext(self.data_source_path)[1].lower()
        data = []
        try:
            if file_extension == '.csv':
                with open(self.data_source_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data = [row for row in reader]
                print(f"Loaded {len(data)} records from CSV: {self.data_source_path}")
            elif file_extension == '.json':
                with open(self.data_source_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"Loaded {len(data)} records from JSON: {self.data_source_path}")
            else:
                print(f"Unsupported file type: {file_extension}. Only .csv and .json are supported.")
                return None
            return data
        except Exception as e:
            print(f"Error loading data from {self.data_source_path}: {e}")
            return None

    def generate_summary_report(self, report_name="summary_report"):
        """Generates a text-based summary report."""
        data = self._load_data()
        if data is None:
            return False

        num_records = len(data)
        if num_records == 0:
            print("No data to generate report.")
            return False

        # Example: Calculate average 'value' if present
        total_value = 0
        value_count = 0
        for record in data:
            if 'value' in record:
                try:
                    total_value += float(record['value'])
                    value_count += 1
                except ValueError:
                    pass # Ignore records where 'value' isn't convertible

        avg_value = total_value / value_count if value_count > 0 else 0

        report_file_path = os.path.join(self.report_output_dir, f"{report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        try:
            with open(report_file_path, 'w', encoding='utf-8') as f:
                f.write(f"--- Data Summary Report ---\n")
                f.write(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Data Source: {self.data_source_path}\n")
                f.write(f"Total Records: {num_records}\n")
                f.write(f"Average 'value': {avg_value:.2f}\n" if value_count > 0 else "No numerical 'value' field found or processed.\n")
                f.write("\n--- First 5 Records Sample ---\n")
                for i, record in enumerate(data[:5]):
                    f.write(f"Record {i+1}: {record}\n")
                f.write("-----------------------------\n")
            print(f"Summary report generated: {report_file_path}")
            return True
        except IOError as e:
            print(f"Error writing report file: {e}")
            return False

    def generate_detailed_csv_report(self, report_name="detailed_report", fields=None):
        """Generates a detailed CSV report from the data."""
        data = self._load_data()
        if data is None or not data:
            print("No data to generate detailed CSV report.")
            return False

        if fields is None:
            # Use all keys from the first record as fields if not specified
            fields = list(data[0].keys()) if data else []

        report_file_path = os.path.join(self.report_output_dir, f"{report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        try:
            with open(report_file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(data)
            print(f"Detailed CSV report generated: {report_file_path}")
            return True
        except IOError as e:
            print(f"Error writing detailed CSV report: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during CSV report generation: {e}")
            return False

if __name__ == "__main__":
    # Create dummy data files for testing
    dummy_csv_data = [
        {"id": "A1", "item": "Laptop", "price": "1200.50", "quantity": "1"},
        {"id": "A2", "item": "Mouse", "price": "25.00", "quantity": "5"},
        {"id": "A3", "item": "Keyboard", "price": "75.99", "quantity": "2"}
    ]
    with open("sample_data.csv", "w", newline='', encoding='utf-8') as f:
        fieldnames = dummy_csv_data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dummy_csv_data)
    print("Dummy sample_data.csv created.")

    dummy_json_data = [
        {"timestamp": "2024-05-01T10:00:00", "event": "Login", "user_id": "user123", "success": True, "value": 1},
        {"timestamp": "2024-05-01T10:05:00", "event": "Purchase", "user_id": "user456", "item_id": "prod_001", "value": 50.75},
        {"timestamp": "2024-05-01T10:10:00", "event": "Login", "user_id": "user789", "success": False, "value": 0}
    ]
    with open("sample_data.json", "w", encoding='utf-8') as f:
        json.dump(dummy_json_data, f, indent=4, ensure_ascii=False)
    print("Dummy sample_data.json created.")

    print("\n--- Generating reports from CSV ---")
    csv_report_gen = ReportGenerator("sample_data.csv")
    csv_report_gen.generate_summary_report("product_summary")
    csv_report_gen.generate_detailed_csv_report("product_details", fields=["id", "item", "price"])

    print("\n--- Generating reports from JSON ---")
    json_report_gen = ReportGenerator("sample_data.json")
    json_report_gen.generate_summary_report("event_summary")
    json_report_gen.generate_detailed_csv_report("event_details")

    # Clean up dummy files
    if os.path.exists("sample_data.csv"):
        os.remove("sample_data.csv")
    if os.path.exists("sample_data.json"):
        os.remove("sample_data.json")
    print("\nCleaned up dummy data files.")
