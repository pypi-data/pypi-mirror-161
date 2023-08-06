import json

def load_json_file(filename):
    """
        loads a json object from file
    """
    json_string = ""
    with open(filename,"r") as file:
        for line in file:
            if json_string == "":
                json_string = line
            else:    
                json_string += "\n" + line
    json_obj = json.loads(json_string)
    return json_obj

def save_json_file(filename, json_value) -> bool:
    """
        save a object as json file
    """
    with open(filename, "w") as file:
        file.write(json.dumps(json_value))
    return True  