import json
from getpass import getpass
import urllib.request
import gitlab


def load_json(json_path: str) -> dict:
    if json_path.startswith("https://"):
        with urllib.request.urlopen(json_path) as url:
            return json.loads(url.read().decode())
    with open(json_path, "r") as json_file:
        return json.load(json_file)


def save_json(json_path: str, resources_dict: dict):
    with open(json_path, "w") as json_file:
        json.dump(resources_dict, json_file, indent=2)


def save_json_to_gitlab(data: dict, gitlab_token: str):
    gl = gitlab.Gitlab(private_token=gitlab_token)
    gl.auth()
    project_id = 38164378 # iseqresources Gitlab ID
    project = gl.projects.get(project_id)
    f = project.files.get(file_path='json/tool.json', ref='main')
    f.content = json.dumps(data)
    f.save(branch='main', commit_message='Update file')


def get_gitlab_token():
    print('''Please enter Gitlab token (https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)''')
    return getpass()


def get_github_token():
    print('''Please enter Github token (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)''')
    return getpass()


def get_jira_email():
    return input('Please enter JIRA email: ')


def get_jira_token():
    print('''Please enter JIRA token (https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)''')
    return getpass()