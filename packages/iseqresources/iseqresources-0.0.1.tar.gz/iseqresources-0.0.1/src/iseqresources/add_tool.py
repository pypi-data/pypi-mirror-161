from utils import utils
import sys


class AddTool:

    def __init__(self, json_file: str):
        self.json_file = json_file
        self.resources_dict = utils.load_json(json_file)

    def add_name(self) -> str:
        return input('Enter a tool/database name: ')

    def add_current_version(self, name: str) -> str:
        format = {
            "github": "(e.g. v1.0.0)",
            "website_with_released": "(e.g. for Ensembl: 107)",
            "website_without_released": "(date in format YYYY/MM/DD)"
        }
        return input(f'Enter a tool/database current version {format.get(name, None)}: ')

    def add_update_task(self) -> list:
        update_task = input('Enter the names of the tasks that should be updated after the new version of the tool (format: task_name_1, task_name_2): ')
        return update_task.replace(" ", "").split(",")

    def add_github_repo(self) -> str:
        github_repo = input('Enter a tool/database repo in github (e.g. https://github.com/lgmgeo/AnnotSV): ')
        try:
            github_repo = github_repo.split("github.com/")[1]
        except IndexError:
            print("Invalid repo url")
            github_repo = self.add_github_repo()
        return github_repo
   
    def add_expected_version(self) -> list:
        expected_version = input('Enter a tool/database expected versions (format: expected_version_1, expected_version_2): ')
        return expected_version.replace(" ", "").split(",")

    def add_url(self, name: str) -> str:
        text = {
            "website_with_released": "Enter a tool/database url and specify where in url expected_version is (e.g. http://ftp.ensembl.org/pub/release-{expected_version}/): ",
            "website_without_released": "Enter (optionally) a tool/database url (e.g. https://civicdb.org/releases): "
        }
        return input(f'{text.get(name, None)}')

    def add_update_every_nth_month(self) -> int:
        return int(input('Enter every how many months it should be updated: '))

    def add_github_tool(self):
        tool_or_database={
            "name": self.add_name(),
            "current_version": self.add_current_version(name="github"),
            "newest_version": "",
            "last_check": "",
            "test": "github",
            "repoWithOwner": self.add_github_repo(),
            "update_task": self.add_update_task()
        }
        self.resources_dict.append(tool_or_database)
        utils.save_json(self.json_file, self.resources_dict)

    def add_website_tool_with_released_version(self):
        tool_or_database={
            "name": self.add_name(),
            "current_version": self.add_current_version(name="website_with_released"),
            "expected_version": self.add_expected_version(),
            "newest_version": "",
            "last_check": "",
            "test": "url-check",
            "url": self.add_url(name="website_with_released"),
            "update_task": self.add_update_task()
        }
        self.resources_dict.append(tool_or_database)
        utils.save_json(self.json_file, self.resources_dict)

    def add_website_tool_without_released_version(self):
        tool_or_database={
            "name": self.add_name(),
            "current_version": self.add_current_version(name="website_without_released"),
            "newest_version": "",
            "update_every_nth_month": self.add_update_every_nth_month(),
            "test": "update-every-nth-month",
            "url": self.add_url(name="website_without_released"),
            "update_task": self.add_update_task()
        }
        self.resources_dict.append(tool_or_database)
        utils.save_json(self.json_file, self.resources_dict)

    def exit(self):
        sys.exit()
