import datetime


class LinkType:
    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name

    name = property(get_name)


class IssueLink:
    def __init__(self, link_relation, key, link_type="Dependancy"):
        self.type = LinkType(link_type)
        self.__setattr__(link_relation, type("obj", (object,), {"key": key}))
        self.key = key


class Project:
    def __init__(self, issue_id):
        self._key = issue_id
        self._name = "TestPrj"

    def get_key(self):
        return self._key

    def set_key(self, new_key):
        self._key = new_key

    def get_name(self):
        return self._name

    def set_name(self, new_name):
        self._name = new_name

    key = property(get_key, set_key)
    name = property(get_name, set_name)


class Status:
    def __init__(self, name):
        self._name = name
        self._resolutiondate = None

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name
        if name in ["Done", "Closed"]:
            self._resolutiondate = datetime.datetime.now()

    def get_resolution_date(self):
        return self._resolutiondate

    name = property(get_name, set_name)
    resolutiondate = property(get_resolution_date)


class Fields:
    def __init__(self, issue_id, status_name):
        self._project = Project(issue_id)
        self._issuelinks = []
        self._status_name = status_name

    def get_project(self):
        return self._project

    def get_status(self):
        return Status(self._status_name)

    def get_issuelinks(self):
        return self._issuelinks

    def set_issuelinks(self, new_issuelinks):
        self._issuelinks = new_issuelinks

    project = property(get_project)
    issuelinks = property(get_issuelinks, set_issuelinks)
    status = property(get_status)


class Issue: 
    def __init__(self, issue_id, status_name="Open", epic_name=None):
        self._key = issue_id
        self._fields = Fields(issue_id.split("-")[0], status_name)
        self._epic_name = epic_name
        self.project = self._fields.project

    def get_fields(self):
        return self._fields

    def get_key(self):
        return self._key

    def get_epic_name(self):
        return self._epic_name


    fields = property(get_fields)
    key = property(get_key)
    epic_name = property(get_epic_name)


class IssueCache:
    def __init__(self, issue):
        self.issue = issue

    def get_fields(self):
        return self.issue._fields

    def get_key(self):
        return self.issue._key

    def get_epic_name(self):
        return self.issue._epic_name

    def get_project(self):
        self.issue._fields.project

    fields = property(get_fields)
    key = property(get_key)
    epic_name = property(get_epic_name)
    project = property(get_project)
    
