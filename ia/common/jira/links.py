def __is_link_external(link, link_type, project_name):
    return hasattr(link, link_type) and not is_internal(getattr(link, link_type).key, project_name)


def is_internal(issue_key, project_name):
    link_key_split = issue_key.split('-')
    return link_key_split[0] == project_name if len(link_key_split)>0 else issue_key.startswith(project_name)


def get_external_dependencies(issue):
    links = []
    project_name = issue.fields.project.key
    for link in issue.fields.issuelinks:
        l_type = 'inwardIssue' if hasattr(link, 'inwardIssue') else 'outwardIssue'
        link.key = getattr(link, l_type).key

        if not is_internal(link.key, project_name):
            if link.type.name == 'Dependancy' and l_type == 'outwardIssue':
                links.append(link)
            elif link.type.name == 'Blocks' and l_type == 'inwardIssue':
                links.append(link)

    return links    


def get_external_blockers(issue):
    blocking_links = []
    project_name = issue.fields.project.key
    for link in issue.fields.issuelinks:
        if link.type.name == "Blocks" and __is_link_external(link, 'inwardIssue', project_name):
            blocking_links.append(getattr(link, 'inwardIssue').key)
    return blocking_links


def get_external_blocked_by(issue):
    blocked_links = []
    project_name = issue.fields.project.key
    for link in issue.fields.issuelinks:
        if link.type.name == "Blocks" and __is_link_external(link, 'outwardIssue', project_name):
            blocked_links.append(getattr(link, 'outwardIssue').key)
    return blocked_links


