import requests
import json
#TODO: Add logging, make daily cron task, output results with date and time stamp. move to server, pip as needed

dataset_url = r"https://data.maryland.gov/resource/rqbf-ng6p.json?$limit=14000"
comparison_json_file = r"E:\DoIT_DetectSocrataJSONChanges\json_files\20180710_0310.json"
# comparison_json_file = r"E:\DoIT_DetectSocrataJSONChanges\json_files\tester.json"

def generate_json_object(dataset_url):
    """
    Makes request to socrata url for dataset and processes response into json objects

    :param dataset_url: url to which the request is made
    :return: json objects in dictionary form
    """
    json_objects = None
    url = dataset_url
    try:
        response = requests.get(url)
    except Exception as e:
        if hasattr(e, "reason"):
            print("build_datasets_inventory(): Failed to reach a server. Reason: {}".format(e.reason))
        elif hasattr(e, "code"):
            print("build_datasets_inventory(): The server couldn't fulfill the request. Error Code: {}".format(e.code))
        exit()
    else:
        json_objects = response.json()
    # with open(r'json_files\20180710_0310.json', 'w') as outfile:
    #     json.dump(json_objects, outfile)
    return json_objects

def load_json(json_file_contents):
    """
    Load .json file contents

    :param json_file_contents: contents of a json file
    :return: the json file contents as a python dictionary
    """
    return json.loads(json_file_contents)

def read_json_file(file_path):
    """
    Read a .json file and grab all contents.

    :param file_path: Path to the .json file
    :return: the contents of the .json file
    """
    with open(file_path, 'r') as file_handler:
        filecontents = file_handler.read()
    return filecontents

response_json_object = generate_json_object(dataset_url=dataset_url)
json_file_lines_list = read_json_file(file_path=comparison_json_file)
file_json_object = load_json(json_file_lines_list)
if len(response_json_object) == len(file_json_object):
    for i in range(len(response_json_object)):
        if response_json_object[i] != file_json_object[i]:
            print(response_json_object[i])
            print(file_json_object[i])
            print("\n")
        else:
            pass
else:
    print("lengths of dictionaries not the same.")
print(response_json_object == file_json_object)


