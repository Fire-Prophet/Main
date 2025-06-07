import csv

class CsvHandler:
    def read_csv(self, file_path):
        data = []
        with open(file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data

    def write_csv(self, file_path, data, fieldnames):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
