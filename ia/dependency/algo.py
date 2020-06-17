'''Dependency factor calculator'''
from ia.common.jira.issue import search_issues


def get_link_key(link):
    return link.inwardIssue.key if hasattr(link, 'inwardIssue') else link.outwardIssue.key


def count_stats(list_of_issues):
    project_count = {}
    epic_count = {}
    link_epic_count = {}

    def add_stat(counter, key):
        if key in counter:
            counter[key] += 1
        else:
            counter[key] = 1    

    for issue_cache in list_of_issues:
        add_stat(epic_count, issue_cache.epic_name)
        for l in issue_cache.linked_issues.values():
            add_stat(project_count, f'{l.project.name} ({l.project.key})')
            add_stat(link_epic_count, l.epic_name)
    return project_count, epic_count, link_epic_count


def count_internal(list_of_issues, internal_projects):
    counter = {'internal': [], 'external': []}

    def has_external_dep(issue_cache):
        for l in issue_cache.linked_issues.values():
            l_project_key = l.project.key
            if l_project_key not in internal_projects:
                # print(f'External {l_project_key}')
                return True
        return False


    for issue_cache in list_of_issues:
        if has_external_dep(issue_cache):
            counter['external'].append(issue_cache.key)
        else:
            counter['internal'].append(issue_cache.key)

    return counter


def count_by_link_type(list_of_issues):
    linked_issues = {}
    seen = set()
    for issue_cache in list_of_issues:
        issue = issue_cache.issue
        project_name = issue.fields.project.key

        for link in issue.fields.issuelinks:
            link_key = get_link_key(link)
            if link_key in seen:
                continue
            seen.add(link_key)
            if not link_key.startswith(project_name):
                linktype = link.type.name
                if linktype in linked_issues:
                    linked_issues[linktype] += 1
                else:
                    linked_issues[linktype] = 1

    return linked_issues


def dependency_factor(jira_access, jql):
    '''After refinement (in backlog or in sprint)'''
    all_issues = search_issues(jira_access, jql)
    all_with_dep = [i for i in all_issues if len(i.load_linked_issues())>0]

    # add issues with Blocked status even have no link (dependency on teams who don't use Jira)
    blocked = [i for i in all_issues if i.status == "Blocked"]

    all_with_dep += [i for i in blocked if i not in all_with_dep]

    percentage = round(len(all_with_dep)*100/len(all_issues), 2) if len(all_issues) else 0
    return percentage, all_issues, all_with_dep
