"""
Detect changes in the response json from Socrata for fixed datasets.

Our open data inspector process is reporting variation in null counts for datasets that have not changed between runs
of the process. In some cases, the data hasn't changed in any way for years. We are trying to determine if the issue
is in the open data inspector process or the response json from Socrata. This script examines two datasets [as of
20180711] that have shown a lot of variation in null counts. This issue does not occur in the majority of the datasets.
The datasets examined by this script represent the few.
"""
#TODO: move to server, pip as needed, make daily cron task

import requests
import json
import os
from collections import namedtuple
import logging
import time

def main():

    # VARIABLES
    Constant = namedtuple("Constant", ["value"])
        # constants
    ROOT_PROJECT_PATH = Constant(value=r"E:\DoIT_DetectSocrataJSONChanges")
    COMPARISON_JSON_FILES_FOLDER = Constant(value=os.path.join(ROOT_PROJECT_PATH.value, "json_files"))
    LOG_FILE = Constant(value=os.path.join(ROOT_PROJECT_PATH.value, r"log_files\LOG.log"))
        # other
    datasets_dict = {"rqbf-ng6p": ("MEA SmartEnergy Renewable Energy",r"https://data.maryland.gov/resource/rqbf-ng6p.json?$limit=14000"),
                     "3r6n-zh6e":("MEA SmartEnergy Transportation",r"https://data.maryland.gov/resource/3r6n-zh6e.json?$limit=4000")}


    # FUNCTIONS
    def gather_comparison_files(file_folder):
        """
        Inventory all comparison json files available present at a particular directory

        :param file_folder: The path to the folder containing all of the comparison json files
        :return: dictionary, key=file name, value=file path
        """
        comparison_files = {}
        for dir, dirs, files in os.walk(file_folder):
            for file in files:
                file_parts = os.path.splitext(file)
                if file_parts[1].lower() == ".json":
                    comparison_files[file_parts[0]] = os.path.join(dir, file)
        return comparison_files

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
                logging.error("build_datasets_inventory(): Failed to reach a server. Reason: {}".format(e.reason))
            elif hasattr(e, "code"):
                logging.error("build_datasets_inventory(): The server couldn't fulfill the request. Error Code: {}".format(e.code))
            exit()
        else:
            json_objects = response.json()
        return json_objects

    def get_applicable_comparison_datasets(master_comparison_dict, dataset_id):
        """
        Isolate the comparison files that are of the dataset being examined

        :param master_comparison_dict: inventory of all comparison json files available
        :param dataset_id: socrata dataset id, known as a 4 by 4
        :return: list of comparison json files applicable to the dataset being examined
        """
        applicable_files_list = []
        for key, value in master_comparison_dict.items():
            if dataset_id in key:
                applicable_files_list.append((key, value))
        return applicable_files_list

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

    def write_json_to_file(date_time_filename_piece, dataset_id, json_objects):
        """
        Create a json file containing json objects from socrata

        :param date_time_filename_piece:  parts of the file name to be created
        :param dataset_id: socrata dataset id, 4 by 4
        :param json_objects: json objects from socrata
        :return: nothing
        """
        filename = r"json_files\{}_{}.json".format(date_time_filename_piece, dataset_id)
        with open(filename, 'w') as outfile:
            json.dump(json_objects, outfile)
        return


    # FUNCTIONALITY
    logging.basicConfig(filename=LOG_FILE.value,level=logging.INFO)
    logging.info("{}".format(time.strftime("%Y%m%d_%H%M")))

    comparison_files_dict = gather_comparison_files(COMPARISON_JSON_FILES_FOLDER.value)
    for dataset_id, name_hyperlink_tuple in datasets_dict.items():
        dataset_name, dataset_hyperlink = name_hyperlink_tuple
        response_json_object = generate_json_object(dataset_url=dataset_hyperlink)
        applicable_comparison_files = get_applicable_comparison_datasets(master_comparison_dict=comparison_files_dict, dataset_id=dataset_id)
        for file_name, file_path in applicable_comparison_files:
            json_file_lines_list = read_json_file(file_path=file_path)
            file_json_object = load_json(json_file_lines_list)
            if len(response_json_object) == len(file_json_object):
                logging.info("JSON objects equal in length. {} \ {}".format(dataset_id, file_name))
                for i in range(len(response_json_object)):
                    if response_json_object[i] != file_json_object[i]:
                        logging.error("{}, Comparison File={}".format(dataset_id,file_name))
                        logging.error("Socrata: {}".format(response_json_object[i]))
                        logging.error("On File: {}".format(file_json_object[i]))
                    else:
                        pass
            else:
                logging.error("Lengths of JSON objects not equal.")
                logging.error(dataset_id)
                logging.error("Socrata: {}".format(len(response_json_object)))
                logging.error("On File: {}".format(len(file_json_object)))

    # __________________________________________________________________
    # For when need to write a new json file for comparison use.
    if False:
        date_time_filename_piece = time.strftime("%Y%m%d_%H%M")
        for key, value in datasets_dict.items():
            dataset_id = key
            dataset_name, dataset_json_request_url = value
            response_json_object = generate_json_object(dataset_url=dataset_json_request_url)
            write_json_to_file(date_time_filename_piece=date_time_filename_piece, dataset_id=dataset_id, json_objects=response_json_object)
    # __________________________________________________________________

if __name__ == "__main__":
    main()