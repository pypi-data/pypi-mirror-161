#!/usr/bin/env python3

import argparse
from tqdm import tqdm
from utils import utils
from iseqresources.check_version import CheckVersion
from iseqresources.add_task_to_jira import AddTaskToJira


__version__ = '0.0.1'


def check_for_new_version(json_file: str, info_json: str):
    resources_dict = utils.load_json(json_file)
    github_token = utils.get_github_token()
    jira_email = utils.get_jira_email()
    jira_token = utils.get_jira_token()
    test_name = {
        "github": lambda : obj.check_github_repo(),
        "url-check": lambda : obj.check_url_with_released_version(),
        "update-every-nth-month": lambda : obj.check_url_without_released_version()
    }
    for tool_or_database in tqdm(resources_dict):
        obj = CheckVersion(tool_or_database, github_token)
        create_task_in_jira = test_name.get(tool_or_database["test"], lambda : "ERROR: Invalid test")()
        # create task in jira if there is new version of tool/database
        if create_task_in_jira:
            jira = AddTaskToJira(tool_or_database, jira_email, jira_token, jira_project_info=info_json)
            jira.add_task_to_jira()
    utils.save_json(json_file, resources_dict)
    return create_task_in_jira


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--input-json', type=str, required=False,
                        help='Json file to which to enter a new field')
    parser.add_argument('--info-json', type=str, required=False,
                        help='Json file with info about JIRA project (server, epic_id and project_id)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    args = parser.parse_args()
    
    check_for_new_version(args.input_json, args.info_json)


if __name__ == "__main__":
    main()
