#!/usr/bin/env python3

import argparse
from iseqresources.add_tool import AddTool


__version__ = '0.0.2'


def info_text():
    return '''Press 0 to exit
Press 1 to add a tool from github
Press 2 to add a tool from website
Press 3 to add a tool from website without specific released version'''


def add_tool_or_database(json_file: str):
    obj = AddTool(json_file)
    switcher={
        0: lambda : obj.exit(),
        1: lambda : obj.add_github_tool(),
        2: lambda : obj.add_website_tool_with_released_version(),
        3: lambda : obj.add_website_tool_without_released_version()
    }
    choice = 1
    while choice != 0:
        print(info_text())
        choice = int(input('Enter a number of your choice: '))
        switcher.get(choice, lambda : "ERROR: Invalid Operation")()


def main():
    parser = argparse.ArgumentParser(description='Add new tool to json file')
    parser.add_argument('--input-json', type=str, required=False,
                        help='Json file to which to enter a new field')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    args = parser.parse_args()

    add_tool_or_database(args.input_json)


if __name__ == "__main__":
    main()
