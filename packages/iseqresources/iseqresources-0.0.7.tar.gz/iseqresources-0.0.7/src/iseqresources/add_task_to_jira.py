from jira import JIRA
from utils import utils


class AddTaskToJira:
    
    def __init__(self, tool: dict, email: str, token: str, jira_project_info: dict):
        self.tool = tool
        self.email = email
        self.token = token
        self.server = jira_project_info["server"]
        self.epic_id = jira_project_info["epic_id"]
        self.project_key = jira_project_info["project_key"]
        self.jira_connection = self.jira_auth()
        self.epic = self.connect_epic()

    def jira_auth(self):
        return JIRA(basic_auth=(self.email, self.token), server=self.server)

    def connect_epic(self):
        return self.jira_connection.issue(self.epic_id)

    def create_issue_dict(self):
        issue_dict = {
            'project': {'key': self.project_key},
            'summary': f'Aktualizacja {self.tool["name"]}',
            'description': 
            f'Obecna wersja narzędzia {self.tool["name"]}: {self.tool["current_version"]}; Najnowsza wersja narzędzia: {self.tool["newest_version"]}',
            'issuetype': {'name': 'Task'}
        }
        return issue_dict

    def create_issue_dict_subtask(self):
        tasks = ", ".join(self.tool["update_task"])
        issue_dict_subtask = {
            'project': {'key': self.project_key},
            'summary': f'Aktualizacja tasków po aktualizacji narzędzia {self.tool["name"]}',
            'description': f'Należy zaktualizować taski: {tasks}',
            'issuetype': {'name': 'Task'}
        }
        return issue_dict_subtask
    
    def create_issue_jira(self, task_or_subtask: str):
        task_or_subtask_dict = {
            "task": lambda : self.create_issue_dict(),
            "subtask": lambda : self.create_issue_dict_subtask()
        }
        return self.jira_connection.create_issue(fields=task_or_subtask_dict.get(task_or_subtask, lambda : "ERROR: Invalid Operation")())

    def add_task_to_jira(self):
        # task
        new_issue = self.create_issue_jira("task")
        new_issue.update(fields={'parent': {'id': self.epic.id}})
        # subtask
        new_issue_subtask = self.create_issue_jira("subtask")
        self.jira_connection.create_issue_link(type='is blocked by', inwardIssue=new_issue_subtask.key, outwardIssue=new_issue.key)
