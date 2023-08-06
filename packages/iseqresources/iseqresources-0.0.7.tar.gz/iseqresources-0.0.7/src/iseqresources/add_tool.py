from utils import utils
import sys
import datetime
import json
import requests

class AddTool:

    def __init__(self, json_file: str, gitlab_token: str):
        self.json_file = json_file
        self.resources_dict = utils.load_json(json_file)
        self.gitlab_token = gitlab_token

    def add_name(self) -> str:
        return input('Enter a tool/database name: ')

    def add_current_version(self, name: str) -> str:
        format = {
            "github": "(e.g. v1.0.0)",
            "url-check": "(e.g. for Ensembl: 107)",
            "update-every-nth-month": "(date in format YYYY/MM/DD)"
        }
        return input(f'Enter a tool/database current version {format.get(name, None)}: ')

    def add_update_task(self) -> list:
        update_task = input('Enter the names of the tasks that should be updated after the new version of the tool (format: task_name_1, task_name_2): ')
        return update_task.replace(" ", "").split(",")

    def add_github_repo(self) -> str:
        github_repo = input('Enter a tool/database repo in github (e.g. https://github.com/lgmgeo/AnnotSV): ')
        if "github.com" in github_repo:
            if self.check_github_repo(github_repo):
                return github_repo
        else:
            print("Invalid repo url")
            return self.add_github_repo()
    
    def check_github_repo(self, repo: str) -> str:
        response = requests.get(repo)
        if response.ok:
            return repo
        else:
            print("Repo does not exist")
            return self.add_github_repo()
   
    def add_expected_version(self) -> list:
        expected_version = input('Enter a tool/database expected versions (format: expected_version_1, expected_version_2): ')
        return expected_version.replace(" ", "").split(",")

    def add_release_day(self) -> str:
        release_day = {
            "NO": "unknown_released",
            "YES": "known_released"
        }
        tool_released_day = input('Does the tool have a known release day (e.g. Clinvar has not https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/)? YES or NO? ')
        return release_day.get(tool_released_day.upper(), None)

    def add_url(self, name: str) -> str:
        text = {
            "url-check_known_released": "Enter a tool/database url and specify where in url expected_version is (e.g. http://ftp.ensembl.org/pub/release-{expected_version}/): ",
            "url-check_unknown_released": "Enter a tool/database url and specify where in url expected_version and release_day is (e.g. https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar_{expected_version}{release_day}.vcf.gz.md5): ",
            "update-every-nth-month": "Enter (optionally) a tool/database url (e.g. https://civicdb.org/releases): "
        }
        if name == "update-every-nth-month":
            return input(f'{text.get(name, None)}')
        return self.check_url_str(input(text.get(name)), name)
    
    def check_url_str(self, url: str, name: str):
        expected_structure = {
            "url-check_known_released": [
                "{expected_version}"
                ],
            "url-check_unknown_released": [
                "{expected_version}",
                "{release_day}"
                ]
        }
        check = [structure in url for structure in expected_structure.get(name, None)]
        if all(item for item in check):
            return url
        else:
            print("Invalid url")
            return self.add_url(name)

    def add_update_every_nth_month(self) -> int:
        return int(input('Enter every how many months it should be updated: '))

    def validate_date(self, date: str):
        try:
            datetime.datetime.strptime(date, '%Y/%m/%d')
            return date
        except ValueError:
            print("Incorrect data format, should be YYYY/MM/DD")
            return self.validate_date(self.add_current_version(name="website_without_released"))

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
        self.ask_about_changes(tool_or_database)
        self.resources_dict.append(tool_or_database)
        if self.gitlab_token:
            utils.save_json_to_gitlab(self.resources_dict, self.gitlab_token)
        else:
            utils.save_json(self.json_file, self.resources_dict)

    def add_website_tool_with_released_version(self):
        known_release_day = self.add_release_day()
        tool_or_database={
            "name": self.add_name(),
            "current_version": self.add_current_version(name="url-check"),
            "expected_version": self.add_expected_version(),
            "known_release_day": known_release_day,
            "newest_version": "",
            "last_check": "",
            "test": "url-check",
            "url": self.add_url(name="url-check_unknown_released") if known_release_day == "unknown_released" else self.add_url(name="url-check_known_released"),
            "update_task": self.add_update_task()
        }
        self.ask_about_changes(tool_or_database)
        self.resources_dict.append(tool_or_database)
        if self.gitlab_token:
            utils.save_json_to_gitlab(self.resources_dict, self.gitlab_token)
        else:
            utils.save_json(self.json_file, self.resources_dict)

    def add_website_tool_without_released_version(self):
        tool_or_database={
            "name": self.add_name(),
            "current_version": self.validate_date(self.add_current_version(name="update-every-nth-month")),
            "newest_version": "",
            "update_every_nth_month": self.add_update_every_nth_month(),
            "test": "update-every-nth-month",
            "url": self.add_url(name="update-every-nth-month"),
            "update_task": self.add_update_task()
        }
        self.ask_about_changes(tool_or_database)
        self.resources_dict.append(tool_or_database)
        if self.gitlab_token:
            utils.save_json_to_gitlab(self.resources_dict, self.gitlab_token)
        else:
            utils.save_json(self.json_file, self.resources_dict)
    
    def ask_about_changes(self, added_tool: dict):
        utils.clear_screen()
        print('''Your tool/database look like this:''')
        print(json.dumps(added_tool, indent=2))
        changes = input('Do you want to make changes? YES or NO? ')
        if changes.upper() == "YES":
            added_tool = self.make_changes(added_tool)
            self.ask_about_changes(added_tool)
    
    def make_changes(self, added_tool: dict):
        field_change = input('Which field you want to change? ')
        known_released = added_tool.get("known_release_day", None)
        url_test = added_tool["test"] + f"_{known_released}" if known_released else added_tool["test"]
        all_fields={
            "name": lambda : self.make_change_in_name(),
            "current_version": lambda : self.make_change_in_current_version(name=added_tool["test"]),
            "expected_version": lambda : self.make_change_in_expected_version(),
            "update_every_nth_month": lambda : self.make_change_in_update_every_nth_month(),
            "known_release_day": lambda : self.make_change_in_known_release_day(),
            "repoWithOwner": lambda : self.make_change_in_repo(),
            "url": lambda : self.make_change_in_url(name=url_test),
            "update_task": lambda : self.make_change_in_update_task()
        }
        added_tool[field_change] = all_fields.get(field_change, lambda : "ERROR: Invalid input")()
        return added_tool
    
    def make_change_in_name(self):
        return self.add_name()
    
    def make_change_in_current_version(self, name: str):
        if name == "update-every-nth-month":
            return self.validate_date(self.add_current_version(name=name))
        return self.add_current_version(name=name)

    def make_change_in_expected_version(self):
        return self.add_expected_version()

    def make_change_in_update_every_nth_month(self):
        return self.add_update_every_nth_month()
    
    def make_change_in_known_release_day(self):
        return self.add_release_day()

    def make_change_in_repo(self):
        return self.add_github_repo()

    def make_change_in_url(self, name: str):
        return self.add_url(name=name)

    def make_change_in_update_task(self):
        return self.add_update_task()        

    def exit(self):
        sys.exit()
