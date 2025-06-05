import json
from datetime import datetime

def log_prediction(input_data, output):
    entry = {
        'time': datetime.now().isoformat(),
        'input': input_data,
        'output': output
    }
    with open('prediction_log.json', 'a') as f:
        f.write(json.dumps(entry) + '\n')
