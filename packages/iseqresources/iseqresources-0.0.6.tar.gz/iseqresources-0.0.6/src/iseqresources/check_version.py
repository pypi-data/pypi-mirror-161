import requests
from packaging import version
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from itertools import dropwhile


class CheckVersion:

    def __init__(self, tool: dict, token: str):
        self.tool = tool
        self.token = token
 
    def get_todays_date(self) -> date:
        today = date.today()
        return today.strftime("%Y/%m/%d")

    def github_auth(self) -> dict:
        return {'Authorization': f'token {self.token}'}
   
    def check_github_repo(self) -> bool:
        currentVersion = version.parse(self.tool["current_version"])
        repoWithOwner= self.tool["repoWithOwner"]
        response = requests.get(f"https://api.github.com/repos/{repoWithOwner}/releases", headers=self.github_auth())
        links = [t["html_url"] for t in response.json() if version.parse(t["tag_name"]) > currentVersion]
        releases = [t["tag_name"] for t in response.json() if version.parse(t["tag_name"]) > currentVersion]
        self.tool["newest_version"] = releases[0] + f" ({links[0]})" if releases else ""
        self.tool["last_check"] = self.get_todays_date()
        return True if releases else False
   
    def check_url_without_released_version(self) -> bool:
        url = self.tool["url"]
        currentVersion = datetime.strptime(self.tool["current_version"], '%Y/%m/%d')
        currentVersion_plus_nth_months = currentVersion + relativedelta(months=+self.tool["update_every_nth_month"])
        currentVersion_plus_nth_months = currentVersion_plus_nth_months.strftime("%Y/%m/%d")
        if self.get_todays_date() > currentVersion_plus_nth_months:
            self.tool["newest_version"] = self.get_todays_date() + f" ({url})"
            return True
        return False

    def check_url_with_released_version(self) -> bool:
        newest_version = ""
        self.tool["last_check"] = self.get_todays_date()
        if self.tool["known_release_day"] == "NO":
            release_days = ["%.2d" % i for i in range(32)]
            for expected_version in self.tool["expected_version"]:
                for release_day in release_days:
                    url = self.tool["url"].format(expected_version=expected_version, release_day=release_day)
                    response = requests.get(url)
                    if response.ok:
                        newest_version = expected_version
                        self.tool["newest_version"] = expected_version + f" ({url})"
                        break
        else:
            for expected_version in self.tool["expected_version"]:
                url = self.tool["url"].format(expected_version=expected_version)
                response = requests.get(url)
                if response.ok:
                    newest_version = expected_version
                    self.tool["newest_version"] = expected_version + f" ({url})"
        if newest_version:
            self.tool["expected_version"] = list(dropwhile(lambda x: x != newest_version, self.tool["expected_version"]))
            return True
        return False
