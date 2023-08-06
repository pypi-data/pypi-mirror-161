#!/usr/bin/env python3

import argparse
from utils import utils
from iseqresources.update_record import UpdateRecord
import sys


__version__ = '0.0.4'


def info_text():
    print('''Press 0 to exit
Press 1 to update a tool/database''')
    return int(input('Enter a number of your choice: '))


def update_tool_record(json_file="https://gitlab.com/intelliseq/iseqresources/-/raw/main/json/tools_and_databases.json"):
    resources_dict = utils.load_json(json_file)
    update_expected_versions = {
        "github": False,
        "url-check": True,
        "update-every-nth-month": False
    }
    choice = 1
    while choice != 0:
        name_to_update = input("Enter name of tool/database to update: ")
        tool_found = False
        for tool_or_database in resources_dict:
            if tool_or_database['name'] == name_to_update:
                obj = UpdateRecord(tool_or_database, update_expected_versions.get(tool_or_database["test"], False))
                obj.update_record()
                tool_found = True
                break
        if not tool_found:
            print("Tool/database not found")
        choice = info_text()
    if json_file.startswith("https://"):
        gitlab_token = utils.get_gitlab_token()
        utils.save_json_to_gitlab(resources_dict, gitlab_token)
    else:
        utils.save_json(json_file, resources_dict)


def main():
    parser = argparse.ArgumentParser(description='Add new tool to json file')
    parser.add_argument('--input-json', type=str, required=False,
                        help='Json file to which to update a new field')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    args = parser.parse_args()

    if args.input_json:
        update_tool_record(args.input_json)
    else:
        update_tool_record()


if __name__ == "__main__":
    main()
