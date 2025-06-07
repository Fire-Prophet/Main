import json

class JsonHandler:
    def dict_to_json(self, data_dict):
        return json.dumps(data_dict, indent=4)

    def json_to_dict(self, json_string):
        return json.loads(json_string)
