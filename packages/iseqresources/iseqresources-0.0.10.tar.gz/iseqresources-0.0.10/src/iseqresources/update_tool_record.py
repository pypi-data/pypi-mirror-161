#!/usr/bin/env python3

import argparse
from utils import utils
from iseqresources.update_record import UpdateRecord
import json
import os


__version__ = '0.0.10'


GITLAB_TOKEN=os.environ.get("GITLAB_TOKEN")


def info_text():
    utils.clear_screen()
    print('''Press 0 to exit
Press 1 to update a tool/database''')
    return int(input('Enter a number of your choice: '))


def tools_in_json(tools_and_databases: list):
    names = []
    for item in tools_and_databases:
        names.append(item['name'])
    return names


def update_tool_record(gitlab_token, json_file="https://gitlab.com/intelliseq/iseqresources/-/raw/main/json/tools_and_databases.json"):
    input_dict = utils.load_json(json_file)
    resources_dict = utils.load_json(json_file)
    update_expected_versions = {
        "github": False,
        "url-check": True,
        "update-every-nth-month": False
    }
    choice = 1
    while choice != 0:
        print("Tools and databases: " + ', '.join(tools_in_json(resources_dict)))
        name_to_update = input("Enter name of tool/database to update: ")
        tool_found = False
        for tool_or_database in resources_dict:
            if tool_or_database['name'] == name_to_update:
                obj = UpdateRecord(tool_or_database, update_expected_versions.get(tool_or_database["test"], False))
                obj.update_record()
                print(f"Tool/database {name_to_update} updated and now look like this:")
                print(json.dumps(tool_or_database, indent=2))
                input("Press enter to continue")
                tool_found = True
                break
        if not tool_found:
            print("Tool/database not found")
            input("Press enter to continue")
        choice = info_text()
    if (input_dict != resources_dict):
        if json_file.startswith("https://"):
            if not gitlab_token:
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
        update_tool_record(gitlab_token=GITLAB_TOKEN,
            json_file=args.input_json)
    else:
        update_tool_record(gitlab_token=GITLAB_TOKEN)


if __name__ == "__main__":
    main()
