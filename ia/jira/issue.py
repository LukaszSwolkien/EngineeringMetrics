"""Helpers to access jira issue fields"""
from jira import JIRAError
from ia.jira.links import get_external_dependencies, is_internal
# from functools import lru_cache
from cachetools import cached

# def get_issue(jira_obj, issue_id, expand_args=None):
#     """Fetch issue data"""
#     return jira_obj.issue(issue_id, expand=expand_args)

#(maxsize=None)
# @lru_cache
issues_cache = {}
@cached(cache = issues_cache)
def get_issue_by_key(jira_obj, issue_key):
    issue_details = []
    jql = f"'key'='{issue_key}'"
    try:
        issue_details = jira_obj.search_issues(jql)
    except JIRAError as error:
        # print(f"error_code:{error.status_code}, error_msg:{error.text}")
        pass
    issue = issue_details[0] if len(issue_details) else None
    return IssueCache(jira_obj, issue) if issue else None

@cached(cache = issues_cache)
def search_issues(jira_access, jql):
    found_issues = jira_access.search_issues(jql, maxResults=500)


    issues = []
    for iss in found_issues:
        issue_wrapper = IssueCache(jira_access, iss)
        issues.append(issue_wrapper)
        # add to cache
        issues_cache[(jira_access, issue_wrapper.key)] = issue_wrapper
    return issues


def get_summary(jira_obj, issue_id):
    issue = jira_obj.issue(issue_id)
    return issue.fields.summary


def get_issue_in_json(jira_obj, issue_id):
    issue_details = None
    error = None
    jql = f"'key'='{issue_id}'"
    try:
        issue_details = jira_obj.search_issues(jql, fields='issue links', json_result=True) #,created,status,reporter  expand='changelog',
    except JIRAError as error:
        error = f"error_code:{error.status_code}, error_msg:{error.text}"

    return {'issue':issue_details, 'error':error}


# def get_epic(jira_obj, issue):
#     if hasattr(issue, 'epic_link'):
#         epic_id = issue.epic_link
#         return get_issue(jira_obj, epic_id)
#     return None


def get_open_sprint(issue):
    if hasattr(issue, "fields") and hasattr(issue.fields, "customfield_11220") and isinstance(issue.fields.customfield_11220, list):
        gh_fields = issue.fields.customfield_11220[0].split(',')
        for f in gh_fields:
            kv = f.split("=")
            if len(kv) > 1 and kv[0] == 'name':
                open_sprint = kv[1]
                return open_sprint
    return ""


def get_components(issue):
    components = []
    if hasattr(issue, "fields") and hasattr(issue.fields, "components") and isinstance(issue.fields.components, list):
        cps = set()
        for c in issue.fields.components:
            cps.add(c.name)
        
        components = list(cps)

    return components


class IssueCache:
    def __init__(self, jira_access, issue):
        self._jira = jira_access
        self._issue = issue
        self._epic_issue = None
        self._epic_name = None
        self._linked_issues = {}  # filtered linked issues (inward, outward, both,..., external, internal, both...)

    def get_jira_access(self):
        return self._jira

    def get_issue(self):
        return self._issue

    def get_fields(self):
        return self.issue.fields
    
    def get_project(self):
        return self.fields.project

    def get_status(self):
        return self.fields.status.name

    def get_epic_name(self):
        if not self._epic_name:
            try:
                epic_key = self.issue.fields.customfield_12120
                self._epic_issue = get_issue_by_key(self._jira, epic_key)
                self._epic_name = self._epic_issue.fields.customfield_12121
            except Exception:
                # keep defaults
                pass
        return self._epic_name

    def get_linked_issues(self):
        return self._linked_issues

    def load_linked_issues(self, max_level=2, filter_out_status=('Done')):
        load_external_issues(self, max_level, filter_out_status)
        return self._linked_issues


    def get_key(self):
        return self.issue.key
    
    jira_access = property(get_jira_access)
    issue = property(get_issue)
    fields = property(get_fields)
    project = property(get_project)
    epic_name = property(get_epic_name)
    key = property(get_key)
    linked_issues = property(get_linked_issues)
    status = property(get_status)


def load_external_issues(issue_cache, max_level, filter_out_status):
    load_external_issues.depth_level = 0

    def load_links(issue_cache):
        jira_access = issue_cache._jira
        links = []
        linked_issues = {}
        issue = issue_cache.issue
        links = get_external_dependencies(issue)
        links += list(get_indirect_external_dependencies(jira_access, issue, links))

        for l in links:
            l_issue = get_issue_by_key(jira_access, l.key)
            if l_issue.status not in filter_out_status:
                linked_issues[l.key] = l_issue

        if load_external_issues.depth_level < max_level:
            load_external_issues.depth_level += 1
            for l_issue_cache in linked_issues.values():
                l_issue_cache._linked_issues = load_links(l_issue_cache)
        return linked_issues

    issue_cache._linked_issues = load_links(issue_cache)


def get_indirect_external_dependencies(jira_access, issue, links_with_external_deps):
    links = set()
    project_name = issue.fields.project.key
    keys_with_external_dep = [l.key for l in links_with_external_deps]
    for link in issue.fields.issuelinks:
        l_type = 'inwardIssue' if hasattr(link, 'inwardIssue') else 'outwardIssue'
        link.key = getattr(link, l_type).key

        if is_internal(link.key, project_name) and (link.type.name == 'Dependancy' and l_type == 'outwardIssue' or link.type.name == 'Blocks' and l_type == 'inwardIssue'):
            if link.key in keys_with_external_dep:
                print(f'Found indirect dependency: {link.key}')
                links.add(link)
            else:
                # Recurtion to check other internal links which may have dependency on the issue with external dependency
                l_issue = get_issue_by_key(jira_access, link.key)
                links = links.union(get_indirect_external_dependencies(jira_access, l_issue, links_with_external_deps))

    return links 