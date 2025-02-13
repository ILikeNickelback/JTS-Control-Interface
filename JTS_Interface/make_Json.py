import json

class Make_json:
    def __init__(self):
        pass
    
    def save_configuration_to_json(self):
        file_name = "something.json"
        configuration = {}
        if file_name:
            with open(file_name, 'w') as json_file:
                json.dump(configuration, json_file, indent=4)


