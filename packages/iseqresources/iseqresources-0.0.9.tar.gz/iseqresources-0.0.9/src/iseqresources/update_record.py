class UpdateRecord:

    def __init__(self, tool: str, update_expected_versions: bool):
        self.tool = tool
        self.update_expected_versions = update_expected_versions
    
    def current_expected_version(self):
        return self.tool["expected_version"]

    def extend_expected_versions(self):
        print(f'Current expected versions: {self.current_expected_version()}')
        new_expected_versions = input('Enter new expected versions (format: expected_version_1, expected_version_2): ')
        new_expected_versions = new_expected_versions.replace(" ", "").split(",")
        self.tool["expected_version"].extend(new_expected_versions)

    def update_current_version(self):
        if self.tool["newest_version"]:
            self.tool["current_version"] = self.tool["newest_version"].split(" (")[0]

    def clear_newest_version(self):
        self.tool["newest_version"] = ""

    def update_record(self):
        self.update_current_version()
        self.clear_newest_version()
        if self.update_expected_versions:
            self.extend_expected_versions()
