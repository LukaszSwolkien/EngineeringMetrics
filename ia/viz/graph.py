from ia.helpers import die
# from ia.jira import IssueCache
from functools import partial
try:
    import pygraphviz as pgv
except ImportError:
    """
    Steps to install graphviz on Mac OS:
    brew install graphviz
    pip install pygraphviz --install-option="--include-path=/usr/local/include/graphviz/" --install-option="--library-path=/usr/local/lib/graphviz"
    """
    die("Please install pygraphviz ")


def save_graph_image(graph, image_file):
    graph.layout(prog='dot')
    # print('Writing to ' + image_file)
    graph.draw(image_file)


def build_graph(issue_cache):
    seen = set() # to prevent infinite recursion in the cyclic graph

    def get_color(typename):
        if typename == 'Epic':
            return 'violet'
        if typename == 'Bug':
            return 'red'
        if typename == 'Test':
            return 'aquamarine'
        if typename == 'Release':
            return "goldenrod2"
        return 'black'

    def get_label(issue_cache):
        epic_name = issue_cache.epic_name
        return f"{issue_cache.key}\n{epic_name}" if epic_name else issue_cache.key

    def get_label_by_key(issue_cache, l_key):
        issue= issue_cache.linked_issues[l_key]
        return get_label(issue)


    def walk(issue_cache, graph):
        seen.add(issue_cache.key)
        issue = issue_cache.issue
        linked_issues = issue_cache.get_linked_issues()
        filtered_links = linked_issues.keys() #[i.key for i in linked_issues]
        fields = issue.fields

        if hasattr(fields, 'issuelinks'):
            for link in fields.issuelinks:
                if hasattr(link, 'outwardIssue'):
                    if (link.outwardIssue.key in filtered_links and (issue.key, link.outwardIssue.key) not in graph.edges()):
                        link_typename = link.outwardIssue.fields.issuetype.name
                        graph.add_node(
                            link.outwardIssue.key, 
                            color=get_color(link_typename), 
                            shape='box', 
                            label=get_label_by_key(issue_cache, link.outwardIssue.key)
                        )
                        graph.add_edge(
                            issue.key, 
                            link.outwardIssue.key, 
                            label=link.type.outward
                        )
                if hasattr(link, 'inwardIssue'):
                    if (link.inwardIssue.key in filtered_links and (link.inwardIssue.key, issue.key) not in graph.edges()):
                        link_typename = link.inwardIssue.fields.issuetype.name
                        graph.add_node(
                            link.inwardIssue.key, 
                            color=get_color(link_typename), 
                            shape='box', 
                            label=get_label_by_key(issue_cache, link.inwardIssue.key)
                        )
                        graph.add_edge(
                            link.inwardIssue.key, 
                            issue.key, 
                            label=link.type.outward
                        )
        
        for l_key, l_issue_cache in linked_issues.items():
            if l_key not in seen:
                # print(l_key)
                walk(l_issue_cache, graph)
        return graph

    graph = pgv.AGraph(strict=False, directed=True)
    
    issue = issue_cache.issue
    issue_typename = issue.fields.issuetype.name
    
    epic_name = issue_cache.epic_name
    if epic_name:
        epic_name = "| Epic: " + epic_name
    graph.graph_attr['label'] = f'{issue.key}: {issue.fields.summary} {epic_name}'
    graph.add_node(issue.key, color=get_color(issue_typename), penwidth='5.0', label=get_label(issue_cache))

    graph = walk(issue_cache, graph)
    return graph


# TODO - remove
# def __build_graph(start_issue_key, jira_access): 
#     seen = []  # since the graph can be cyclic we need to prevent infinite recursion

#     issue_fetcher = partial(ticket.get_issue, jira_access)
#     issue_fetcher_by_key = partial(ticket.get_issue_by_key, jira_access)
    
#     issue = issue_fetcher(start_issue_key)
#     project_name = issue.fields.project.key
#     is_external = partial(lambda prj, key: not key.startswith(prj), project_name)

#     def get_color(typename):
#         if typename == 'Epic':
#             return 'violet'
#         if typename == 'Bug':
#             return 'red'
#         if typename == 'Test':
#             return 'aquamarine'
#         if typename == 'Release':
#             return "goldenrod2"
#         return 'black'

#     def get_epic_name(issue):
#         epic_name = ""
#         try:
#             # try to find linked epic issue via custom field and get epic name
#             epic_key = issue.fields.customfield_12120
#             epic_issue = issue_fetcher_by_key(epic_key)
#             epic_name = f'{epic_issue.fields.customfield_12121}'
#         except Exception as e:
#             # print(e)
#             # just ignore epic_name
#             pass
#         return epic_name

#     def get_label(issue):
#         epic_name = get_epic_name(issue)
#         return f"{issue.key}\n{epic_name}" if epic_name else issue.key

#     def get_label_by_key(issue_key):
#         issue = issue_fetcher_by_key(issue_key)
#         return get_label(issue)
    
#     build_graph.depth_level = 0

#     def walk(issue, graph, max_level=2, check_subtasks=False):  # TODO: Decide - Maybe always append children but only for given fixVersion ??
#         build_graph.depth_level += 1
#         seen.append(issue.key)
#         children = []
#         fields = issue.fields
#         if hasattr(fields, 'epic_id'):
#             epickey = fields.epic_id
#             if (epickey, issue.key) not in graph.edges():
#                 graph.add_edge(epickey, issue.key, color='violet', label='epic')
#                 children.append(epickey)
#         if check_subtasks and hasattr(fields, 'subtasks'):
#             for subtask in fields.subtasks:
#                 if (issue.key, subtask.key) not in graph.edges():
#                     graph.add_edge(issue.key, subtask.key, color='blue', label='subtask', penwidth='0.5')
#                     children.append(subtask.key)
#         if hasattr(fields, 'issuelinks'):
#             for link in fields.issuelinks:
#                 if hasattr(link, 'outwardIssue'): # and link.type.name == "Blocks":
#                     if is_external(link.outwardIssue.key) and (issue.key, link.outwardIssue.key) not in graph.edges():
#                         link_typename = link.outwardIssue.fields.issuetype.name
#                         graph.add_node(link.outwardIssue.key, color=get_color(link_typename), shape='box', label=get_label_by_key(link.outwardIssue.key))
#                         graph.add_edge(issue.key, link.outwardIssue.key, label=link.type.outward)
#                         children.append(link.outwardIssue.key)
#                 if hasattr(link, 'inwardIssue'): # and link.type.name == "Blocks":
#                     if is_external(link.inwardIssue.key) and (link.inwardIssue.key, issue.key) not in graph.edges():
#                         link_typename = link.inwardIssue.fields.issuetype.name
#                         graph.add_node(link.inwardIssue.key, color=get_color(link_typename), shape='box', label=get_label_by_key(link.inwardIssue.key))
#                         graph.add_edge(link.inwardIssue.key, issue.key, label=link.type.outward)
#                         children.append(link.inwardIssue.key)
        
#         if build_graph.depth_level < max_level:
#             # dig deeper into related issues (linked, subtasks and epics)
#             for child in (x for x in children if x not in seen):
#                 child_issue = issue_fetcher(child)
#                 # child_project_name = child_issue.fields.project.key
#                 walk(child_issue, graph, max_level)
#         return graph

#     graph = pgv.AGraph(strict=False, directed=True)
    
#     issue_typename = issue.fields.issuetype.name
    
#     epic_name = get_epic_name(issue)
#     if epic_name:
#         epic_name = "| Epic: " + epic_name
#     graph.graph_attr['label'] = f'{start_issue_key}: {issue.fields.summary} {epic_name}'
#     graph.add_node(start_issue_key, color=get_color(issue_typename), penwidth='5.0', label=get_label(issue))

#     graph = walk(issue, graph)
#     return graph

