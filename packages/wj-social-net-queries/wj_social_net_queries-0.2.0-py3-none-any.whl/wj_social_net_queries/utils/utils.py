import json
import logging
from urllib.request import urlretrieve

import pandas as pd

from ..utils.constants.constants import CSV, JSON


def log_api_execption(function_name: str, code_status: int, details: dict):
    json_formatted_str = json.dumps(details, indent=2)
    logging.error(
        function_name + "\nCode: " + str(code_status) + "\n" + json_formatted_str
    )


def safe_data_in_file(path: str, data, file_type: str):
    if file_type == JSON:
        pass
    elif file_type == CSV:
        safe_data_on_csv(path=path, data=data)


# TODO decorator for exceptions
def safe_data_on_csv(path: str, data: list, columns: list):
    try:
        if len(data) == 0:
            logging.info("No info")
            return
        df = pd.DataFrame(data)
        print(df)
        df.to_csv(path, mode="a", sep="|", index=False)
        logging.info("saved")
    except Exception as e:
        logging.error("safe_dict_on_csv :: " + str(e))


def save_data_on_json(path: str, data):
    try:
        jsonFile = open(path, "r")
        tmp_data = json.loads(jsonFile)
        jsonFile.close()
        tmp_data.update(data)
        jsonFile = open(path, "w+")
        jsonFile.write(json.dumps(tmp_data))
        jsonFile.close()
    except:
        jsonFile = open(path, "w+")
        jsonFile.write(json.dumps(data))
        jsonFile.close()


def download_image(url, filename):
    try:
        urlretrieve(url, filename)
    except Exception as e:
        print(e)
