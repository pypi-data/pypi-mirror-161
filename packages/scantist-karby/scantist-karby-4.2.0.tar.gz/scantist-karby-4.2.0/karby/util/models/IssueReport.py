
field_names = [
            "Library",
            "Library Version",
            "Public ID",
            "Scope",
            "Score",
            "File Path",
            "Patched Version",
            "Latest Component Version",
            "Issue Source",
        ]

class IssueReport:
    def __init__(self, library, library_version, public_id, scope="-"):
        self.info = {
            "Library": library,
            "Library Version": library_version,
            "Public ID": public_id,
            "Scope": scope,
            "Score": "",
            "File Path": "",
            "Patched Version": "",
            "Latest Component Version": "",
            "Issue Source": "",
        }

    def get_field(self):
        return self.field_names

    def set_field(self, key, value):
        if self.info.__contains__(key):
            self.info[key] = value
            return 0
        else:
            return 1

    def get_hash(self):
        return f"{self.info['Library']} {self.info['Library Version']} {self.info['Public ID']}"
