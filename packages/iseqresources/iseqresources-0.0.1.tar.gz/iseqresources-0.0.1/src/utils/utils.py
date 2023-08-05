import json
from getpass import getpass

def load_json(json_path: str) -> dict:
    with open(json_path, "r") as json_file:
        return json.load(json_file)


def save_json(json_path: str, resources_dict: dict):
    with open(json_path, "w") as json_file:
        json.dump(resources_dict, json_file, indent=2)


def get_github_token():
    print('''Please enter github token (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)''')
    return getpass()


def get_jira_email():
    return input('Please enter JIRA email: ')


def get_jira_token():
    print('''Please enter JIRA token (https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)''')
    return getpass()