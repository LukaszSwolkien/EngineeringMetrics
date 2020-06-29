
class LinkType:
    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name
    
    name = property(get_name)


class IssueLink:
    def __init__(self, link_relation, key, link_type="Dependancy"):
        self.type = LinkType(link_type)
        self.__setattr__(link_relation, type('obj', (object,) ,{'key': key}))
        self.key = key


class Project:
    def __init__(self, issue_id):
        self._key = issue_id

    def get_key(self):
        return self._key

    def set_key(self, new_key):
        self._key = new_key
    key = property(get_key, set_key)


class Status:
    def __init__(self, name):
        self.name = name

class Fields:
    def __init__(self, issue_id):
        self._project = Project(issue_id)
        self._issuelinks = []
    
    def get_project(self):
        return self._project
    
    def get_status(self):
        return Status('Dummy')

    def get_issuelinks(self):
        return self._issuelinks

    def set_issuelinks(self, new_issuelinks):
        self._issuelinks = new_issuelinks

    project = property(get_project)
    issuelinks = property(get_issuelinks, set_issuelinks)
    status = property(get_status)


class Issue:
    def __init__(self, issue_id):
        self._key = issue_id
        self._fields = Fields(issue_id.split('-')[0])
    
    def get_fields(self):
        return self._fields

    def get_key(self):
        return self._key

    fields = property(get_fields)
    key = property(get_key)
